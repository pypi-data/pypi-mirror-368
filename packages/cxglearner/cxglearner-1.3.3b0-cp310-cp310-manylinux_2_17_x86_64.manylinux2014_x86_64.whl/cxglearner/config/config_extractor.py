import argparse


def extractor_opts(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--worker_num", default=1, type=int,help="Number of workers to generate candidates.")
    parser.add_argument("--allow_cuda", default=False, type=bool, help="Whether to allow the use of CUDA for candidate "
                                                                       "generation.")
    parser.add_argument("--number_per_gpu", default=0, type=int, help="The number of tasks to assign for each GPU.")
    parser.add_argument("--gpu_indices", default=None, type=list, help="List of ranks of each process.")
    parser.add_argument("--gpu_cpu_ratio", default=1., type=float, help="The ratio of data processed by each GPU to "
                                                                        "the CPU.")
    parser.add_argument("--mp_mode", default="high-precision", type=str, help="The parallel mode.")

    parser.add_argument("--min_length", default=3, type=int, help="The minimum length of cxg candidate.")
    parser.add_argument("--max_length", default=7, type=int, help="The maximum length of cxg candidate.")

    parser.add_argument("--ref_num", default=50, type=int, help="The refernece number for determining the candidates.")
    parser.add_argument("--beam_size", default=20, type=int, help="The number of beam size for determining the "
                                                                  "candidates.")
    parser.add_argument("--candidate_mode", default="dynamic", choices=["dynamic", "static", "nucleus"],
                        type=str, help="The mode for determining the candidates.")
    parser.add_argument("--neucleus_k", default=20, type=int, help="The k value for neucleus mode.")
    parser.add_argument("--neucleus_p", default=0.6, type=float, help="The p value for neucleus mode.")
    parser.add_argument("--score_accum", default="multiply", help="The operator to accumulate sequence scores.")
    parser.add_argument("--rpt_debug", default=None, help="The tool to determine the hyper-parameters.")

    parser.add_argument("--candidate_path", default='cache/candidate.pt', type=str, help="The path of candidate "
                                                                                         "storage.")

    parser.add_argument("--pruner", default=None,  help=" Pruning strategy selector")

    return parser


if __name__ == '__main__':
    print('>> Extractor')
    args = extractor_opts().parse_args()
