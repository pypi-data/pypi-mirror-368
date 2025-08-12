import argparse


def experiment_opts(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--name", type=str, default="learner_default", help="Experiment name for recording.")
    parser.add_argument("--language", type=str, default="english", help="Language for acquisition.")
    parser.add_argument("--lang", type=str, default="en", help="Language abbr for acquisition.")
    log_opts(parser)

    # Global Params
    parser.add_argument("--corpus_path", type=str, default="cache/gpt-wikibook.pt", help="Path of the corpus.")
    parser.add_argument("--save_path", type=str, default=None, help="Path for saving all files.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")

    return parser


def log_opts(parser):
    parser.add_argument("--log_path", type=str, default=None, help="Log file path, default no output file.")
    parser.add_argument("--log_level", choices=["ERROR", "INFO", "DEBUG", "NOTSET"], default="INFO", help="Console log level. Verbosity: ERROR < INFO < DEBUG < NOTSET")
    parser.add_argument("--log_file_level", choices=["ERROR", "INFO", "DEBUG", "NOTSET"], default="INFO", help="Log file level. Verbosity: ERROR < INFO < DEBUG < NOTSET")


if __name__ == '__main__':
    print('>> Experiment')
    args = experiment_opts().parse_args()
