from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.config.config import Config
from cxglearner.utils.utils_log import init_logger
from cxglearner.encoder.encoder import Encoder

import pytest

config = Config(DefaultConfigs.eng)
logger = init_logger(config)
encoder = Encoder(config, logger)

sample_sentence = "The nearest tube stations are Charing Cross and Embankment, and numerous bus routes serve the western end of the street."
raw_results = encoder.encode(sample_sentence, raw=True, need_ids=False)
results = encoder.encode(sample_sentence, raw=False, need_ids=True, need_mask=True)
print(raw_results)
print(results)

# batch encoding
sample_sentences = ["The nearest tube stations are Charing Cross and Embankment, and numerous bus routes serve the western end of the street.", "She ate an apple yesterday."]
raw_results = encoder.encode_batch(sample_sentences, raw = True, need_ids=False)
results = encoder.encode_batch(sample_sentences, raw = False)
print(raw_results)
print(results)

# Align test
sample_sentence4align = "NanoSonic’s Metal Rubber™ is an electrically conductive and flexible elastomer."
results4align = encoder.encode(sample_sentence4align, raw=False, need_ids=True)
print(results4align)

sample_sentence4align2 = "So South cashes the hearts and then the ♠K, ♠A and ♠Q."
results4align2 = encoder.encode(sample_sentence4align2, raw=False, need_ids=True)
print(results4align2)


@pytest.fixture
def sample_sentence():
    sample_sentence = "The nearest tube stations are Charing Cross and Embankment, and numerous bus routes serve the western end of the street."
    return sample_sentence


@pytest.fixture
def sample_sentences():
    sample_sentences = ["The nearest tube stations are Charing Cross and Embankment, and numerous bus routes serve the western end of the street.", "She ate an apple yesterday."]
    return sample_sentences


def test_encoding(sample_sentence):
    raw_results = encoder.encode(sample_sentence, raw=True, need_ids=False)
    results = encoder.encode(sample_sentence, raw=False, need_ids=True)
    print(raw_results)
    print(results)
    assert len(raw_results['lexical']) ==  len(raw_results['upos']['spaCy']) ==  len(raw_results['upos']['stanza']) == len(raw_results['upos']['rdrpos'])


def test_batch_encoding(sample_sentences):
    raw_results = encoder.encode_batch(sample_sentences, raw=True, need_ids=False)
    results = encoder.encode_batch(sample_sentences, raw=False, need_ids=True)
    print(raw_results)
    print(results)
    for i in range(len(sample_sentences)):
        assert len(raw_results[i]['lexical']) ==  len(raw_results[i]['upos']['spaCy']) ==  len(raw_results[i]['upos']['stanza']) == len(raw_results[i]['upos']['rdrpos'])
