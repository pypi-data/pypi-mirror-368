CONFIG_CHECK = {
    # Experiment
    "experiment_name": [['experiment', 'experimentName'], str, True],
    'experiment_language': [['experiment', 'language'], str, False],
    'experiment_lang': [['experiment', 'langAbbr'], str, False],
    'experiment_corpus_path': [['experiment', 'corpusPath'], str, True],
    'experiment_seed': [['experiment', 'seed'], int, False],
    "experiment_save_path": [['experiment', 'savePath'], str, False],
    'experiment_log_path': [['experiment', 'logPath'], str, False],
    # Encoder
    'encoder_levels': [['encoder', 'levels'], dict, True],
    'encoder_clean_args': [['encoder', 'cleanerArgs'], dict, False],
    'encoder_worker_num': [['encoder', 'workerNum'], int, False],
    'encoder_whole_word_flag': [['encoder', 'wholeWordFlag'], str, True],
    "encoder_back_ratio": [['encoder', 'backRatio'], float, False],
    "encoder_search_ratio": [['encoder', 'searchRatio'], float, False],
    "encoder_corpus_shuffle": [['encoder', 'corpusShuffle'], bool, False],
    # LM
    'lm_model_name': [['lm', 'modelName'], str, False],
    'lm_wandb_name': [['lm', 'wandbName'], str, False],
    'lm_dataset_path': [['lm', 'datasetPath'], str, False],
    'lm_output_path': [['lm', 'outputModelPath'], str, False],
    'lm_deep_init': [['lm', 'deepInit'], bool, False],
    'lm_whole_word_masking': [['lm', 'wholeWordMasking'], bool, False],
    'lm_allow_skip': [['lm', 'allowSkip'], bool, False],
    'lm_loader_num': [['lm', 'loaderNum'], int, False],
    'lm_platform': [['lm', 'platform'], dict, False],
    'lm_selection_probs': [['lm', 'selectionProbs'], dict, False],
    'lm_fp16': [['lm', 'fp16'], bool, False],
    'lm_batch_size': [['lm', 'batchSize'], int, False],
    'lm_learning_rate': [['lm', 'learningRate'], float, False],
    'lm_epochs_num': [['lm', 'epochsNum'], int, False],
    'lm_config_path': [['lm', 'configPath'], str, False],
    'lm_offbyone': [['lm', 'offbyone'], bool, False],
    'lm_save_checkpoint_steps': [['lm', 'saveSteps'], int, False],
    # Extractor
    'extractor_worker_num': [['extractor', 'workerNum'], int, False],
    'extractor_allow_cuda': [['extractor', 'allowCuda'], bool, False],
    'extractor_number_per_gpu': [['extractor', 'numberPerGpu'], int, False],
    'extractor_gpu_indices': [['extractor', 'gpuIndices'], list, False],
    'extractor_gpu_cpu_ratio': [['extractor', 'gpuCpuRatio'], float, False],
    'extractor_mp_mode': [['extractor', 'mpMode'], str, False],
    'extractor_min_length': [['extractor', 'minLength'], int, False],
    'extractor_max_lengt': [['extractor', 'maxLength'], int, False],
    'extractor_ref_num': [['extractor', 'refNum'], int, False],
    'extractor_beam_size': [['extractor', 'beamSize'], int, False],
    'extractor_candidate_mode': [['extractor', 'candidateMode'], str, False],
    'extractor_candidate_path': [['extractor', 'candidatePath'], str, False],
    'extractor_pruner': [['extractor', 'pruner'], dict, False],
    'extractor_score_accum': [['extractor', 'scoreAccum'], str, False],
    'extractor_rpt_debug': [['extractor', 'rptDebug'], dict, False],
    'extractor_neucleus_k': [['extractor', 'neucleusK'], int, False],
    'extractor_neucleus_p': [['extractor', 'neucleusP'], float, False],
    # Learner
    'learner_object': [['learner', 'object'], dict, False],
    'learner_candidate_cxs_path': [['learner', 'candidateCxsPath'], str, False],
    'learner_do_preprocess': [['learner', 'doPreprocess'], bool, False],
    'learner_heuristic_search': [['learner', 'heuristicSearch'], str, False],
    'learner_init_state_method': [['learner', 'initStateMethod'], str, False],
    'learner_metric_weight':  [['learner', 'metricWeight'], dict, False],
    'learner_wandb_name': [['learner', 'wandbName'], str, False],
    'learner_recorder_path': [['learner', 'recorderPath'], str, False],
    # Parser
    'parser_backend': [['parser', 'backend'], str, False],
}

CONFIG_MAP = {
    'experiment_': 'experiment',
    'encoder_': 'encoder',
    'lm_': 'lm',
    'extractor_': 'extractor',
    'learner_': 'learner',
    'parser_': 'parser'
}

# Allow the arguments be the dict
LEGAL_PAR = ['levels', 'cleanerArgs', 'selectionProbs', 'pruner', 'metricWeight', 'object', 'rptDebug']
