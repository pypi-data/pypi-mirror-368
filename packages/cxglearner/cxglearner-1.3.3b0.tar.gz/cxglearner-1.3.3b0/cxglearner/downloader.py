import re
import argparse
import requests
from datetime import datetime
import shutil
import threading
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .utils.predefine import DOWNLOADER_BASE_URL
from .utils.misc import get_latest_version, clean_version
from typing import Dict, List, Optional, Union, Tuple


class Downloader:
    BASE_URL = DOWNLOADER_BASE_URL
    JSON_DATA_URL = urljoin(BASE_URL, "data/data.json")
    CACHE_DIR = Path.home() / ".cache" / "CxGLearner"

    def __init__(self, verbose: bool = False, cache_dir: Path = None):
        self.verbose = verbose
        self.data: Dict[str, Dict[str, str]] = {}
        if cache_dir is not None:
            self.CACHE_DIR = Path(cache_dir)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        if self.verbose:
            print(f"[Downloader] {message}")

    def fetch_data(self) -> Dict[str, Dict[str, str]]:
        try:
            self.log(f"Fetching data from: {self.JSON_DATA_URL}")
            response = requests.get(self.JSON_DATA_URL, timeout=10)
            response.raise_for_status()
            self.data = response.json()
            return self.data
        except requests.RequestException as e:
            self.log(f"Failed to fetch JSON data: {e}")
            self.log("Falling back to HTML parsing")
            return self.parse_html_data()

    def parse_html_data(self) -> Dict[str, Dict[str, str]]:
        try:
            self.log(f"Fetching HTML from: {self.BASE_URL}")
            response = requests.get(self.BASE_URL, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            json_viewer = soup.find('div', {'id': 'json-viewer'})

            if not json_viewer:
                raise ValueError("JSON viewer section not found")

            self.data = {}

            for lang_block in json_viewer.find_all('div', class_='json-item'):
                lang_key = lang_block.find('div', class_='json-key')
                if not lang_key:
                    continue

                lang_match = re.search(r'([a-z]{2})\s', lang_key.text, re.IGNORECASE)
                if not lang_match:
                    continue

                lang_code = lang_match.group(1).lower()
                lang_data = {}
                lang_data["defaults"] = ""

                for version_block in lang_block.find_all('div', class_='version-block'):
                    version_key = version_block.find('div', class_='json-key')
                    version_url = version_block.find('a', class_='json-value')

                    if version_key and version_url:
                        version_text = version_key.text.strip()

                        version_match = re.search(r'([\d.]+)', version_text)
                        version_num = version_match.group(1) if version_match else version_text

                        url = version_url['href']

                        if "default" in version_text.lower():
                            lang_data["defaults"] = version_num

                        lang_data[version_text] = url

                if lang_data["defaults"]:
                    lang_data["latest"] = lang_data["defaults"]

                self.data[lang_code] = lang_data

            return self.data
        except Exception as e:
            self.log(f"HTML parsing failed: {e}")
            return {}

    def get_available_languages(self) -> List[str]:
        if not self.data:
            self.fetch_data()
        return list(self.data.keys())

    def get_versions(self, lang: str, add_special: bool = False) -> List[str]:
        if not self.data:
            self.fetch_data()

        if lang not in self.data:
            raise ValueError(f"Language '{lang}' not available")
        specials = ["defaults", "latest"] if add_special else []
        return [clean_version(v) for v in self.data[lang].keys()
                if v not in ["defaults", "latest"]] + specials

    def get_download_url(self, lang: str, version: str = "default") -> str:
        if not self.data:
            self.fetch_data()

        if lang not in self.data:
            raise ValueError(f"Language '{lang}' not available")

        lang_data = self.data[lang]

        if version == "default":
            if not lang_data.get("defaults"):
                raise ValueError(f"No default version found for language '{lang}'")
            for key in lang_data:
                if key != "defaults" and key != "latest" and lang_data["defaults"] in key:
                    return lang_data[key]
            if lang_data["defaults"].startswith("http"):
                return lang_data["defaults"]
            else:
                return lang_data[lang_data["defaults"]]

        if version == "latest":
            return lang_data["latest"]

        if version in lang_data:
            return lang_data[version]

        matched_versions = [v for v in lang_data.keys()
                            if version.lower() in v.lower() and v not in ["defaults", "latest"]]

        if matched_versions:
            return lang_data[matched_versions[0]]

        raise ValueError(f"Version identifier '{version}' not found for language '{lang}'")

    def download(self, lang: str, version: str = "latest",
                 output_dir: Optional[Union[str, Path]] = None) -> Path:
        url = self.get_download_url(lang, version)
        self.log(f"Download URL: {url}")

        output_dir = Path(output_dir) if output_dir else self.CACHE_DIR
        if version in ["default", "latest"]:
            download_dir = output_dir / lang / version
            download_dir.mkdir(parents=True, exist_ok=True)

            if any(download_dir.iterdir()):
                self.log(f"Data already exists in {download_dir}. Skipping download.")
                return download_dir

            temp_dir = download_dir / "temp"
            temp_dir.mkdir(exist_ok=True)

            self.log(f"Downloading data for {lang} ({version})...")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            zip_filename = url.split("/")[-1] or "data.zip"
            zip_path = temp_dir / zip_filename
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.log(f"Extracting data to temporary directory {temp_dir}...")
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            zip_path.unlink()

            extracted_items = list(temp_dir.iterdir())
            if not extracted_items:
                raise RuntimeError("No files extracted from zip")

            content_dir = None
            for item in extracted_items:
                if item.is_dir():
                    if re.match(r'.*\d+\.\d+.*', item.name):
                        content_dir = item
                        break

            if not content_dir:
                for item in extracted_items:
                    if item.is_dir():
                        content_dir = item
                        break

            actual_version = "unknown"
            if content_dir:
                version_match = re.search(r'(\d+(?:\.\d+)+)', content_dir.name)
                if version_match:
                    actual_version = version_match.group(1)
                else:
                    version_match = re.search(r'/(\d+(?:\.\d+)+)\.zip$', url)
                    if version_match:
                        actual_version = version_match.group(1)
                    else:
                        actual_version = datetime.now().strftime("%Y%m%d")
            else:
                version_match = re.search(r'/(\d+(?:\.\d+)+)\.zip$', url)
                if version_match:
                    actual_version = version_match.group(1)
                else:
                    actual_version = datetime.now().strftime("%Y%m%d")

            if content_dir:
                self.log(f"Moving content from {content_dir} to {download_dir}")
                for content_item in content_dir.iterdir():
                    shutil.move(str(content_item), str(download_dir))

                content_dir.rmdir()
            else:
                for item in extracted_items:
                    shutil.move(str(item), str(download_dir))

            shutil.rmtree(temp_dir)

            version_file = download_dir / "version"
            with open(version_file, 'w') as f:
                f.write(actual_version)

            self.log(f"Download and extraction complete: {download_dir}")
            self.log(f"Actual version: {actual_version}")
            return download_dir

        else:
            safe_version = re.sub(r'[^\w.-]', '_', version)
            download_dir = output_dir / lang
            download_dir.mkdir(parents=True, exist_ok=True)

            # if any(download_dir.iterdir()):
            #     self.log(f"Data already exists in {download_dir}. Skipping download.")
            #     return download_dir

            self.log(f"Downloading data for {lang} ({version})...")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            zip_filename = url.split("/")[-1] or "data.zip"
            zip_path = download_dir / zip_filename
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.log(f"Extracting data to {download_dir}...")
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)

            zip_path.unlink()

            self.log(f"Download and extraction complete: {download_dir}")
            return download_dir / safe_version

    def get_cache_data(self, lang: str = 'eng', output_dir: Optional[Union[str, Path]] = None):
        cached_files = self.list_cache()
        if lang not in cached_files:
            self.log("No available construction inventory resources corresponding to `{lang}` can currently be found "
                  f"locally. Try to obtain available language resources remotely. You can also terminate the process"
                  f" and specify the `construction_path`.")
            if lang in self.get_available_languages():
                download_cache_dir = self.download(lang, output_dir=output_dir)
                return download_cache_dir
            else:
                raise Exception(f"The resources corresponding to the language `{lang}` cannot be found. "
                                f"The currently supported languages are {self.get_available_languages()}.")
        else:
            download_cache_dir = cached_files[lang]
            if "latest" in download_cache_dir:
                self.update(lang, "latest")
                download_cache_dir = download_cache_dir["latest"]
            else:
                version = get_latest_version(download_cache_dir.keys())
                download_cache_dir = download_cache_dir[version]
            return download_cache_dir

    def get_cache_version(self, lang: str = "eng", version: str = "latest", output_dir: Optional[Union[str, Path]] = None):
        cached_files = self.list_cache()
        if lang not in cached_files:
            self.log("No available construction inventory resources corresponding to `{lang}` can currently be found "
                     f"locally. Try to obtain available language resources remotely. You can also terminate the process"
                     f" and specify the `construction_path`.")
            if lang not in self.get_available_languages():
                raise Exception(f"The resources corresponding to the language `{lang}` cannot be found. "
                                f"The currently supported languages are {self.get_available_languages()}.")
        cached_files[lang] = {}
        if version in cached_files[lang]:
            return cached_files[lang][version]
        else:
            ava_versions = self.get_versions(lang, add_special=True)
            if version in ava_versions:
                return self.download(lang, version=version, output_dir=output_dir)
            else:
                raise Exception(f"The specified version {version} for `{lang}` does not exist. "
                                f"The currently supported version is `{ava_versions}`.")

    def list_cache(self, output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Dict[str, Path]]:
        cache_dir = Path(output_dir) if output_dir else self.CACHE_DIR
        cache = {}

        if not cache_dir.exists():
            self.log(f"Cache directory does not exist: {cache_dir}")
            return {}

        for lang_dir in cache_dir.iterdir():
            if lang_dir.is_dir():
                lang = lang_dir.name
                cache[lang] = {}
                for version_dir in lang_dir.iterdir():
                    if version_dir.is_dir():
                        if any(version_dir.iterdir()):
                            version = version_dir.name
                            original_version = re.sub(r'(\d+)_(\d+)', r'\1.\2', version)
                            cache[lang][original_version] = version_dir

        return cache

    def _extract_version_from_url(self, url: str) -> str:
        version_match = re.search(r'/(\d+(?:\.\d+)+)\.zip$', url)
        if version_match:
            return version_match.group(1)

        version_match = re.search(r'/(\d+(?:\.\d+)+)/', url)
        if version_match:
            return version_match.group(1)

        return datetime.now().strftime("%Y%m%d")

    def _version_to_tuple(self, version: str) -> tuple:
        try:
            return tuple(map(int, version.split('.')))
        except ValueError:
            return (hash(version),)

    def check_update(self, lang: str, version: str = "latest",
                     output_dir: Optional[Union[str, Path]] = None) -> Tuple[bool, str, str]:

        if version not in ["latest", "default"]:
            raise ValueError("check_update only supports 'latest' or 'default' versions")

        output_dir = Path(output_dir) if output_dir else self.CACHE_DIR
        download_dir = output_dir / lang / version

        try:
            url = self.get_download_url(lang, version)
            remote_version = self._extract_version_from_url(url)
        except Exception as e:
            self.log(f"Failed to get remote version: {e}")
            return False, "", ""

        version_file = download_dir / "version"
        if not version_file.exists():
            self.log(f"No local version found for {lang}/{version}")
            return True, "", remote_version

        try:
            with open(version_file, 'r') as f:
                local_version = f.read().strip()
        except Exception as e:
            self.log(f"Failed to read local version: {e}")
            return True, "", remote_version

        local_tuple = self._version_to_tuple(local_version)
        remote_tuple = self._version_to_tuple(remote_version)

        has_update = remote_tuple > local_tuple
        self.log(
            f"Update check: {lang}/{version} - local: {local_version}, remote: {remote_version}, update: {has_update}")

        return has_update, local_version, remote_version

    def _input_with_timeout(self, prompt: str, timeout: float = 10.0) -> str:
        result = []

        def get_input():
            try:
                response = input(prompt)
                result.append(response)
            except EOFError:
                result.append("")

        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True
        input_thread.start()
        input_thread.join(timeout)

        if input_thread.is_alive():
            print("\nTimeout reached. Continuing without update.")
            return ""

        return result[0] if result else ""

    def update(self, lang: str, version: str = "latest",
               output_dir: Optional[Union[str, Path]] = None,
               force: bool = False, interactive: bool = True) -> bool:
        if version not in ["latest", "default"]:
            raise ValueError("update only supports 'latest' or 'default' versions")

        output_dir = Path(output_dir) if output_dir else self.CACHE_DIR
        download_dir = output_dir / lang / version

        if not force:
            has_update, local_version, remote_version = self.check_update(lang, version, output_dir)

            if not has_update:
                self.log(f"No update needed for {lang}/{version} (local: {local_version}, remote: {remote_version})")
                return False

            if interactive:
                prompt = (
                    f"New version available for {lang}/{version}: {local_version} -> {remote_version}\n"
                    f"Do you want to update? [Y/n] (timeout in 10s): "
                )
                response = self._input_with_timeout(prompt, 10.0).strip().lower()

                if response in ["n", "no"]:
                    self.log("Update cancelled by user")
                    return False
                elif response not in ["", "y", "yes"]:
                    self.log("Invalid response, cancelling update")
                    return False
        else:
            self.log(f"Forcing update for {lang}/{version}")

        self.log(f"Removing old version: {download_dir}")
        if download_dir.exists():
            shutil.rmtree(download_dir)

        try:
            self.log(f"Downloading new version for {lang}/{version}")
            self.download(lang, version, output_dir)
            return True
        except Exception as e:
            self.log(f"Update failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="CxGLearner Data Downloader - Download language construction data"
    )
    parser.add_argument(
        "action",
        choices=["list-langs", "list-versions", "download", "list-cache"],
        help="Action to perform: list-langs, list-versions, download, or list-cache"
    )
    parser.add_argument(
        "--lang", "-l",
        help="Language code (e.g., 'en', 'zh')"
    )
    parser.add_argument(
        "--version", "-v",
        default="default",
        help="Version to download: 'default', 'latest', or specific version identifier (e.g., '1.1 (dedup)')"
    )
    parser.add_argument(
        "--output", "-o",
        help="Custom output directory (default: ~/.cache/CxGLearner)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--cache-dir",
        help="Custom cache directory to list (only for list-cache action)"
    )

    args = parser.parse_args()
    downloader = Downloader(verbose=args.verbose)

    try:
        if args.action == "list-langs":
            langs = downloader.get_available_languages()
            print("Available languages:")
            for lang in langs:
                print(f" - {lang}")

        elif args.action == "list-versions":
            if not args.lang:
                raise ValueError("Language must be specified for list-versions action")

            versions = downloader.get_versions(args.lang)
            print(f"Available versions for {args.lang}:")
            for version in versions:
                print(f" - {version}")

        elif args.action == "download":
            if not args.lang:
                raise ValueError("Language must be specified for download action")

            result = downloader.download(
                lang=args.lang,
                version=args.version,
                output_dir=args.output
            )
            print(f"Data successfully downloaded to: {result}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()