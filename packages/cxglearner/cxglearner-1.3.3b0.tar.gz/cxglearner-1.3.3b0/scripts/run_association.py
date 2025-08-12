import torch

from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.utils.utils_log import init_logger
from cxglearner.config.config import Config
from cxglearner.encoder.encoder import Encoder
from cxglearner.lm.association.association import Association


config = Config(DefaultConfigs.eng)
logger = init_logger(config)
encoder = Encoder(config, logger)
asso_handler = Association(config, logger, encoder=encoder)
level_map = {x: i for i, x in enumerate(encoder.ava_levels)}

example_sentence = "stay for the"
select_mask = ['lexical', 'lexical', 'lexical']
select_mask = [level_map[level] for level in select_mask]
select_mask_2 = ['lexical', 'upos', 'lexical']
select_mask_2 = [level_map[level] for level in select_mask_2]

encoded = encoder.encode(example_sentence, need_ids=True)
inputs_1 = [element[select_mask[i]] for i, element in enumerate(encoded)]
inputs_2 = [element[select_mask_2[i]] for i, element in enumerate(encoded)]
inputs1_tensor = torch.Tensor(inputs_1).type(torch.int64)
inputs2_tensor = torch.Tensor(inputs_2).type(torch.int64)

# dynamic candidates
candidate_dynamic = asso_handler.compute_candidate(inputs_1)
print(candidate_dynamic)

# top-k candidates
canidates_1 = asso_handler.compute_association(inputs_1)
candidate_1_key = {encoder.convert_ids_to_tokens(element[0]): element[1] for element in canidates_1}
canidates_2 = asso_handler.compute_association(inputs_2)
candidate_2_key = {encoder.convert_ids_to_tokens(element[0]): element[1] for element in canidates_2}
print(candidate_1_key)
print(candidate_2_key)

# association
candidate_token = encoder.tokenize(' night')
candidate_ids = encoder.convert_tokens_to_ids(candidate_token)
association_1 = asso_handler.compute_association(inputs_1, candidate_ids)
association_2 = asso_handler.compute_association(inputs_2, candidate_ids)
print(association_1)
print(association_2)

# representation
hidden = asso_handler.lm_head.encode_construction(inputs1_tensor)

# similarity
similarity = asso_handler.lm_head.compute_similarity(inputs1_tensor, inputs2_tensor)
print(similarity)
