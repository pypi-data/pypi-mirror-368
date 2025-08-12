import os
import pickle
from logging import Logger
from typing import Union, Optional, List, Any
from tqdm import tqdm
import random

from ffrecord import FileReader, FileWriter

from .multi_processor import MultiProcessor, mp_allocate_data
from .misc import set_seed
from .predefine import BACKGROUND_SUFFIX

SHUFFLE_BUCKET = 50
SHUFFLE_PREFIX = "cache-shuffle-"


def merge_dataset(dataset_path: Union[str, os.PathLike], workers_num: int, cache_dir: str = './cache') -> int:
    # Merge datasets.
    dataset_num = 0
    dataset_writer = open(dataset_path, "wb")
    for i in range(workers_num):
        tmp_dataset_counter_reader = open("{}/dataset-tmp-".format(cache_dir) + str(i) + "-counter.txt", "r")
        tmp_dataset_num = eval(tmp_dataset_counter_reader.readlines()[0])
        dataset_num += tmp_dataset_num
        print("{}/dataset-tmp-".format(cache_dir) + str(i) + ".pt contains : {} instances".format(tmp_dataset_num))
        tmp_dataset_counter_reader.close()

        tmp_dataset_reader = open("{}/dataset-tmp-".format(cache_dir) + str(i) + ".pt", "rb")
        while True:
            tmp_data = tmp_dataset_reader.read(2**20)
            if tmp_data:
                dataset_writer.write(tmp_data)
            else:
                break
        tmp_dataset_reader.close()
        os.remove("{}/dataset-tmp-".format(cache_dir) + str(i) + ".pt")
        os.remove("{}/dataset-tmp-".format(cache_dir) + str(i) + "-counter.txt")
    dataset_writer.close()
    return dataset_num


def count_lines(file_path: Union[str, os.PathLike]) -> int:
    lines_num = 0
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(2**20)
            if not data:
                break
            lines_num += data.count(b'\n')
    return lines_num


def serialize(sample):
    """ Serialize a sample to bytes or bytearray

    You could use anything you like to serialize the sample.
    Here we simply use pickle.dumps().
    """
    return pickle.dumps(sample)


def convert_ffrecord(dataset_path: Union[str, os.PathLike], data_num: int,
                     logger: Optional[Logger] = None, remove_old_file: Optional[bool] = True) -> Union[str, os.PathLike]:
    counter = 0
    if logger is not None: logger.info('Convert .pt file to ffrecord format ...')
    else: print('Convert .pt file to ffrecord format ...')
    datasetff_path = dataset_path.replace('.pt', '.ffr')
    dataset_reader = open(dataset_path, "rb")
    writer = FileWriter(datasetff_path, data_num)
    try:
        while True:
            instance = pickle.load(dataset_reader)
            counter += 1
            writer.write_one(serialize(instance))
    except EOFError:
        if logger is not None: logger.info('Reach Last Line of %s' % dataset_path)
        else: print('Reach Last Line of %s' % dataset_path)
    if logger is not None: logger.info('Check for differences, counter = %d, temporary = %d' % (counter, data_num))
    else: print('Check for differences, counter = %d, temporary = %d' % (counter, data_num))
    dataset_reader.close()
    writer.close()
    if remove_old_file: os.remove(dataset_path)
    if logger is not None: logger.info('FFR file has been saved at %s' % datasetff_path)
    else: print('FFR file has been saved at %s' % datasetff_path)
    return datasetff_path


def convert_dataset_suffix(path: Union[str, os.PathLike], logger: Optional[Logger] = None) -> Union[str, os.PathLike]:
    prefix = ''
    if path.startswith('.'): prefix = path.split('/')[0] + '/'
    if not os.path.exists(path) and path.split('.')[-1] in ['pt', 'pth']:
        splitted = path.split('.')
        splitted[-1] = '.ffr'
        ffr_path = prefix + ''.join(splitted)
        if os.path.exists(ffr_path): return ffr_path
        else:
            if logger is not None: logger.warning("Unable to find the location of the dataset from `{}`.".format(path))
            else: print("Unable to find the location of the dataset from `{}`.".format(path))
            return path
    else: return path


def determine_dataset_name(config, path: Union[os.PathLike, str], logger: Optional[Logger] = None,
                           suffix: Optional[str]=BACKGROUND_SUFFIX) -> str:
    if 'extractor' not in config.__dict__: return path
    if config.encoder.back_ratio < 0.: return path
    name_wosuffix = get_name_wosuffix(path, logger)
    return name_wosuffix + '{}.pt'.format(suffix)


def create_cache_dir(base_path: os.PathLike, folder: os.PathLike, suffix: Optional[str] = None
                     ) -> Union[os.PathLike, str]:
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    comp_path = os.path.join(base_path, folder if suffix is None else '{}_{}'.format(folder, suffix))
    if not os.path.exists(comp_path):
        os.mkdir(comp_path)
    return comp_path


def merge_candidates(dataset_path: Union[str, os.PathLike], workers_num: int, logger: Optional[Logger] = None,
                     cache_dir: str = './cache') -> int:
    # Merge candidates.
    cadidate_num = 0
    cadidate_writer = open(dataset_path, "wb")
    for i in range(workers_num):
        tmp_candidate_counter_reader = open("{}/candidate-tmp-".format(cache_dir) + str(i) + "-counter.txt", "r")
        tmp_candidate_num = eval(tmp_candidate_counter_reader.readlines()[0])
        cadidate_num += tmp_candidate_num
        if logger is not None:
            logger.info("{}/candidate-tmp-".format(cache_dir) + str(i) + ".pt contains : {} "
                                                                         "candidates".format(tmp_candidate_num))
        else:
            print("{}/candidate-tmp-".format(cache_dir) + str(i) + ".pt contains : {} "
                                                                   "candidates".format(tmp_candidate_num))
        tmp_candidate_counter_reader.close()

        tmp_candidate_reader = open("{}/candidate-tmp-".format(cache_dir) + str(i) + ".pt", "rb")
        while True:
            tmp_data = tmp_candidate_reader.read(2**20)
            if tmp_data:
                cadidate_writer.write(tmp_data)
            else:
                break
        tmp_candidate_reader.close()
        os.remove("{}/candidate-tmp-".format(cache_dir) + str(i) + ".pt")
        os.remove("{}/candidate-tmp-".format(cache_dir) + str(i) + "-counter.txt")
    cadidate_writer.close()
    return cadidate_num


@MultiProcessor
def shuffle_coprpus(proc_id: int, worker_num: int, corpus_path: str, lines_num: int, cache_dir: str, seed: int) -> None:
    # Prepare
    set_seed(seed)
    pos, document = 0, []
    start, end = mp_allocate_data(lines_num, proc_id, worker_num)
    bucket_base = proc_id * SHUFFLE_BUCKET
    # Check for cache files
    for index in range(SHUFFLE_BUCKET):
        cache_file_name = "{}/{}".format(cache_dir, SHUFFLE_PREFIX) + str(bucket_base + index) + ".pt"
        if os.path.exists(cache_file_name):
            os.remove(cache_file_name)
    data_bucket_writer = ["{}/{}".format(cache_dir, SHUFFLE_PREFIX) + str(bucket_base + index)  + ".pt" for index in range(SHUFFLE_BUCKET)]
    # Shuffle
    with open(corpus_path, mode="r", encoding="utf-8") as f:
        while pos < start:
            f.readline()
            pos += 1
        for _ in tqdm(range(start, end), desc='Shuffling with proc {}'.format(proc_id), position=proc_id):
            line = f.readline()
            if not line.strip():
                selected_file = random.choice(data_bucket_writer)
                selected_fp = open(selected_file, "a", encoding='utf-8')
                for doc_line in document: selected_fp.write(doc_line + '\n')
                selected_fp.write('\n')
                selected_fp.close()
                document = []
                continue

            if len(line.strip()) > 0:
                document.append(line.strip())
        if len(document) > 0:
            selected_file = random.choice(data_bucket_writer)
            selected_fp = open(selected_file, "a", encoding='utf-8')
            for doc_line in document: selected_fp.write(doc_line)
            selected_fp.write('\n')
            selected_fp.close()


def merge_shuffled_corpus(worker_num: int, shuffled_path: Union[os.PathLike, str], cache_dir: str, seed: int) -> None:
    set_seed(seed)
    bucket_num = worker_num * SHUFFLE_BUCKET
    data_bucket_reader = ["{}/{}".format(cache_dir, SHUFFLE_PREFIX) + str(index) + ".pt" for index in range(bucket_num)
                          if os.path.exists("{}/{}".format(cache_dir, SHUFFLE_PREFIX) + str(index) + ".pt" )]
    if os.path.exists(shuffled_path): os.remove(shuffled_path)
    shuffled_writer = open(shuffled_path, "wb")
    while len(data_bucket_reader) > 0:
        comb_index = random.randint(0, len(data_bucket_reader) - 1)
        data_reader = open(data_bucket_reader[comb_index], "rb")
        while True:
            bucket_corpus_data = data_reader.read(2 ** 20)
            if not bucket_corpus_data:  break
            shuffled_writer.write(bucket_corpus_data)
        data_reader.close()
        del data_bucket_reader[comb_index]
    shuffled_writer.close()
    # Clean cache files
    for index in range(bucket_num):
        cache_file_name = "{}/{}".format(cache_dir, SHUFFLE_PREFIX) + str(index) + ".pt"
        if not os.path.exists(cache_file_name): continue
        os.remove(cache_file_name)


def find_split_line(corpus_path: Union[os.PathLike, str], line_num: int, total_lines_num: int) -> Union[None, int]:
    split_num = 0
    try:
        data_reader = open(corpus_path, mode="r", encoding="utf-8")
        while split_num < line_num:
            data_reader.readline()
            split_num += 1
        while split_num < total_lines_num:
            line = data_reader.readline()
            if not line.strip(): break
            split_num += 1
        data_reader.close()
    except: split_num = None
    return split_num


def get_name_wosuffix(path_name: Union[os.PathLike, str], logger: Optional[Logger] = None) -> Union[str, os.PathLike]:
    file_wosuffix = path_name.split('.')[-1]
    if len(file_wosuffix) < 1:
        if logger is not None: logger.warning("The name of corpus seems to lack a file suffix.")
        else: print("The name of corpus seems to lack a file suffix.")
    else: file_wosuffix = path_name[:-len(file_wosuffix)-1]
    return file_wosuffix


def get_pruner_prefix(path_name: Union[os.PathLike, str]) -> str:
    from .predefine import PRUNER_SUFFIX_GROUP
    for suffix in PRUNER_SUFFIX_GROUP: path_name = path_name.replace(suffix, '')
    return path_name


def write_ffrecord_file(file_path: Union[str, os.PathLike], data: Any,
                   logger: Optional[Logger] = None) -> Union[str, os.PathLike]:
    info_msg = f'Save at {file_path} with ffrecord format ...'
    if logger is not None: logger.info(info_msg)
    else: print(info_msg)
    writer = FileWriter(file_path, len(data))
    for element in tqdm(data, desc="saving files"):
        writer.write_one(serialize(element))
    writer.close()
    return file_path


def read_ffrecord_file(file_path: Union[str, os.PathLike], check_data: Optional[bool] = True,
                       desc: Optional[str] = None) -> Any:
    data = []
    reader = FileReader(file_path, check_data)

    def read_data(index_inner: int) -> Any:
        element = tuple(pickle.loads(reader.read_one(index_inner)))
        data.append(element)

    if desc is not None:
        for index in tqdm(range(reader.n), desc=desc): read_data(index)
    else:
        for index in range(reader.n): read_data(index)
    reader.close()
    return data


def get_data_nums(path: Union[os.PathLike, str], check_data: Optional[bool] = False, logger: Optional[Logger] = None) -> int:
    try:
        number = FileReader(path, check_data).n
    except Exception as e:
        if logger is not None: logger.error(e)
        raise Exception(e)
    return number


def read_corpus(file_path: Union[str, os.PathLike], check_data: Optional[bool] = True,
                       desc: Optional[str] = None) -> Any:
    data = []
    reader = FileReader(file_path, check_data)

    def read_data(index_inner: int) -> Any:
        element = pickle.loads(reader.read_one(index_inner))
        data.append(element)

    if desc is not None:
        for index in tqdm(range(reader.n), desc=desc): read_data(index)
    else:
        for index in range(reader.n): read_data(index)
    reader.close()
    return data
