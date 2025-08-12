import argparse


def encoder_opts(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--levels", default=None, help="Type of encoding levels for a specific language..")
    parser.add_argument("--clean_args", default={}, help="Args for cleantext package.")
    parser.add_argument("--worker_num", default=1, help="Number of workers to process the dataset.")
    parser.add_argument("--whole_word_flag", type=str, default=None, help="The parser used to determine the whole word.")
    parser.add_argument("--back_ratio", type=float, default=-1.0, help="Divide the proportion of background "
                                "corpus, if it is a negative value, no division is made.")
    parser.add_argument("--search_ratio", type=float, default=-1.0, help="Divide the proportion of candidate searching "
                                "corpus, if it is a negative value, no division is made.")
    parser.add_argument("--corpus_shuffle", type=bool, default=False, help="Randomly shuffle the documents in corpus.")
    return parser


if __name__ == '__main__':
    print('>> Encoder')
    args = encoder_opts().parse_args()
