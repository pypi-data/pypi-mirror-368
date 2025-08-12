import argparse


def parser_opts(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--backend", type=str, default="ac", help="Backend for parser.")
    parser.add_argument("--maximum_cxs_per_sentence", type=int, default=50, help="Maximum number of constructions per sentence.")
    parser.add_argument("--specified_cxs", type=bool, default=False, help="Whether to use specified constructions.")
    return parser


if __name__ == '__main__':
    print('>> Parser')
    args = parser_opts().parse_args()
