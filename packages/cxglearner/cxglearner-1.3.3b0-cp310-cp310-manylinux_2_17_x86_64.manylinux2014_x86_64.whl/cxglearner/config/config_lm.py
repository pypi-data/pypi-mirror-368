import argparse


def lm_opts(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--model_name", type=str, default="GPT_Base", help="Type of pre-trained language model.")
    parser.add_argument("--dataset_path", type=str, default=None, help="Path of the preprocessed dataset.")
    parser.add_argument("--output_path", type=str, default='checkpoints/gpt2-base-prob.pt', help="Path of the output model.")
    parser.add_argument("--config_path", type=str, default="models/GPT_Base", help="Config file of model hyper-parameters.")

    # Training and saving options.
    parser.add_argument("--epochs_num", type=int, default=5, help="Total epochs.")
    parser.add_argument("--save_checkpoint_steps", type=int, default=10000, help="Specific steps to save model checkpoint.")
    parser.add_argument("--report_steps", type=int, default=100, help="Specific steps to print prompt.")
    parser.add_argument("--accumulation_steps", type=int, default=1, help="Specific steps to accumulate gradient.")
    parser.add_argument("--seq_length", type=int, default=128, help="Init sequence length in training process, note seq_length <= max_seq_legth.")
    parser.add_argument("--batch_size", type=int, default=64, help="Training batch size. The actual batch_size is [batch_size x world_size x accumulation_steps].")
    parser.add_argument("--dropout", type=float, default=0.1, help="Dropout value.")
    parser.add_argument("--short_seq_prob", type=float, default=0.0, help="Probability of truncating sequence. The larger value, the higher probability of using short (truncated) sequence.")

    # Preprocess options.
    tokenizer_opts(parser)

    optimization_opts(parser)

    # Model options.
    model_opts(parser)
    parser.add_argument("--data_processor", choices=["gpt", "mlm"], default="gpt", help="The data processor of the pretraining model.")
    parser.add_argument("--deep_init", type=bool, default=True, help="Scaling initialization of projection layers by a factor of 1/sqrt(2N). Necessary to large models.")

    # Masking options.
    parser.add_argument("--whole_word_masking", type=bool, default=True, help="Whole word masking.")
    parser.add_argument("--selection_probs", default=None, help="The probs for selecting different level slots.")

    # Visualization options.
    parser.add_argument("--wandb_name", default=None, help="Wandb project name.")

    # GPU options.
    parser.add_argument("--server", default="local", type=str, choices=['local', 'remote'], help="Mode for training.")
    parser.add_argument("--master_ip", default="tcp://localhost:12345", type=str, help="IP-Port of master for training.")
    parser.add_argument("--backend", choices=["nccl", "gloo"], default="nccl", type=str, help="Distributed backend.")
    parser.add_argument("--world_size", type=int, default=1, help="Total number of processes (GPUs) for training.")
    parser.add_argument("--gpu_ranks", default=[], nargs='+', type=int, help="List of ranks of each process.")

    # Accelerater
    parser.add_argument("--pin_memory", default=True, type=bool, help="Activate pin memory option for dataloader.")
    parser.add_argument("--loader_num", default=4, type=int, help="Number of workers for dataloader.")
    parser.add_argument("--tf32", action='store_true', help="Whether to use TF32 for tensor core (this feature may not support your GPU card).")
    parser.add_argument("--torch_compile", action='store_true', help="Whether to use torch.compile (this feature need pytorch >= 2.0.0), not available now.")

    return parser


def tokenizer_opts(parser):
    parser.add_argument("--tokenizer", type = str, default="gpt", help="tokenizer type")
    parser.add_argument("--vocab_path", default=None, type=str, help="Path of the vocabulary file.")
    parser.add_argument("--merges_path", default=None, type=str, help="Path of the merges file.")
    parser.add_argument("--spm_model_path", default=None, type=str, help="Path of the sentence piece model.")
    parser.add_argument("--do_lower_case", type=bool, default=True, help="Whether to lower case the input")


def model_opts(parser):
    parser.add_argument("--embedding", choices=["word", "word_pos", "word_pos_seg"], default="word_pos", help="Emebdding type.")
    parser.add_argument("--max_seq_length", type=int, default=512, help="Max sequence length for word embedding.")
    parser.add_argument("--relative_position_embedding", type=bool, default=False, help="Use relative position embedding.")
    parser.add_argument("--share_embedding", type=bool, default=False, help="Shared embedding and target embedding parameters.")
    parser.add_argument("--remove_embedding_layernorm", type=bool, default=False, help="Remove layernorm on embedding.")
    parser.add_argument("--factorized_embedding_parameterization", action="store_true", help="Factorized embedding parameterization.")
    parser.add_argument("--encoder", choices=["transformer"], default="transformer", help="Encoder type.")
    parser.add_argument("--mask", choices=["fully_visible", "causal"], default="causal", help="Mask type.")
    parser.add_argument("--layernorm_positioning", choices=["pre", "post"], default="post", help="Layernorm positioning.")
    parser.add_argument("--feed_forward", choices=["dense", "gated"], default="dense", help="Feed forward type, specific to transformer model.")
    parser.add_argument("--relative_attention_buckets_num", type=int, default=32, help="Buckets num of relative position embedding.")
    parser.add_argument("--remove_attention_scale", type=bool, default=False, help="Remove attention scale.")
    parser.add_argument("--remove_transformer_bias", type=bool, default=False, help="Remove bias on transformer layers.")
    parser.add_argument("--layernorm", choices=["normal", "t5"], default="normal", help="Layernorm type.")
    parser.add_argument("--parameter_sharing", action="store_true", help="Parameter sharing.")
    parser.add_argument("--has_residual_attention", action="store_true", help="Add residual attention.")
    parser.add_argument("--has_lmtarget_bias", action="store_true", help="Add bias on output_layer for lm target.")
    parser.add_argument("--target", choices=["lm", "mlm"], default="lm", nargs='+', help="The training target of the pretraining model.")
    parser.add_argument("--tie_weights", type=bool, default=True, help="Tie the word embedding and softmax weights.")
    parser.add_argument("--offbyone", type=bool, default=False, help="Whether to pad the softmax function.")


def optimization_opts(parser):
    parser.add_argument("--clip_gradient", type=float, default=-1., help="Clipped gradient for model using torch.nn.utils.clip_grad_norm_(), value < 0 stands for invalid.")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate.")
    parser.add_argument("--warmup", type=float, default=0.1, help="Warm up value.")
    parser.add_argument("--fp16", type=bool, default=False, help="Whether to use 16-bit (mixed) precision (through NVIDIA apex) instead of 32-bit.")
    parser.add_argument("--fp16_opt_level", choices=["O0", "O1", "O2", "O3" ], default='O1', help="For fp16: Apex AMP optimization level selected in ['O0', 'O1', 'O2', and 'O3']. See details at https://nvidia.github.io/apex/amp.html")
    parser.add_argument("--optimizer", choices=["adamw", "adafactor", "lamb"], default="adamw", help="Optimizer type.")
    parser.add_argument("--scheduler", choices=["linear", "cosine", "cosine_with_restarts", "polynomial","constant", "constant_with_warmup", "None"], default="linear", help="Scheduler type.")

if __name__ == '__main__':
    print('>> Language Modelling')
    args = lm_opts().parse_args()
