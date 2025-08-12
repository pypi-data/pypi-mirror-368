import argparse


def learner_opts(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--object", default=None, help="Object function for optimization.")
    parser.add_argument("--heuristic_search", default=None, help="")
    parser.add_argument("--candidate_cxs_path", default=None, help="The path of candidate cxs list.")
    parser.add_argument("--do_preprocess", type=bool, default=True, help="Whether to preprocess the data.")
    parser.add_argument("--init_state_method", type=str, default="random", help="Init method for the state.")
    parser.add_argument("--metric_weight", default=None, help="Weights setting for metrics.")

    parser.add_argument("--wandb_name", default=None, help="Wandb project name.")
    parser.add_argument("--recorder_path", default=None, help="The path of recorder file (.ffr).")
    
    return parser


if __name__ == '__main__':
    print('>> Learner')
    args = learner_opts().parse_args()
