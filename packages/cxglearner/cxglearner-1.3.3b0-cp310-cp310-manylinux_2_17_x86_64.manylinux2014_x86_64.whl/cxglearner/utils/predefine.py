DEFAULT_ASSOCIA_SIZE = 10

SHUFFLED_SUFFIX = '_shuffled'
BACKGROUND_SUFFIX = '-background'
CANDIDATE_SUFFIX = '-candidate'
LEARNER_SUFFIX = '-learner'
CANDIDATE_COUNTER_SUFFIX = '-counter'
FREQUENCY_PRUNER_SUFFIX = '-freq-pruner'
VERTICAL_PRUNER_SUFFIX = '-vertical-pruner'
HORIZONTAL_PRUNER_SUFFIX = '-horizontal-pruner'
NORMALIZED_FREQ_SUFFIX = '-normalized-pruner'
CONSTRUCTIONS_FILE_NAME = 'constructions.ffr'
SLOTS_GRAPH_FOR_PRUNER_SUFFIX = '-pgraph'
PRUNER_SUFFIX_GROUP = [FREQUENCY_PRUNER_SUFFIX,
                       VERTICAL_PRUNER_SUFFIX, HORIZONTAL_PRUNER_SUFFIX]

FFR_FILE_SUFFIX = '.ffr'
PT_FILE_SUFFIX = '.pt'


MP_TEMPO_FILE_VERTICAL_PRUNE_CLUSTER = 'tempo-prune-vertical_clusters'

MP_TEMPO_FILE_COMPUTE_DISTANCES = 'tempo-compute-syn_distances'
MP_TEMPO_FILE_COMPUTE_DISTANCES_CAND = 'tempo-compute-syn_distances_cand'
MP_TEMPO_FILE_COMPUTE_DISTANCES_LTOT = 'tempo-compute-syn_distances_ltot'
MP_TEMPO_FILE_COMPUTE_DISTANCES_GRAPH = 'tempo-compute-syn_distances_graph'
MP_TEMPO_FILE_COMPUTE_SYNSSEMCL = 'tempo-compute-cl'
SYMSEM_DISTANCS_FILE_NAME = 'cached_syn_dists'

CXS_LINK_SYMBOL = '--'

MP_LEARNER_UNPACK_FILE_NAME_TEMPLATE = 'mp_unpacked_{}.pt'
MP_LEARNER_UNPACK_FILE_NAME_FFR_TEMPLATE = 'mp_unpacked_{}.ffr'
MP_LEARNER_MDLGRAPH_FILE_NAME_TEMPLATE = 'mp_mdlgraph_{}.graph'
MP_LEARNER_MDLGRAPH_STAT_FILE_NAME_TEMPLATE = 'mp_mdlstat_{}.stat'

DOWNLOADER_BASE_URL = "https://learner.xlxw.org/"

HF_ENDPOINT = 'https://huggingface.co'
HF_MAGIC_ENDPOINT = 'https://hf-mirror.com'

