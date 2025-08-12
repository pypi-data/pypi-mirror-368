import os
from logging import Logger
from typing import Union, Tuple, List, Any
import unicodedata
from collections import OrderedDict
import numpy as np
from pathlib import Path

from .encode_vocab import *

try:
    import spacy
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False

try:
    import stanza
    from stanza import Document as Document
    STANZA_AVAILABLE = True
except:
    STANZA_AVAILABLE = False

try:
    from ..tools.parsers.RDRPOSTagger.pSCRDRtagger.RDRPOSTagger import RDRPOSTagger
    from ..tools.parsers.RDRPOSTagger.Utility.Utils import readDictionary
    RDR_AVAILABLE = True
except:
    RDR_AVAILABLE = False

RDR_LANGUAGE_MAP = {
    'eng': "English"
}

RDR_VOCAB = {
    'upos': glossary_universal,
    'xpos': glossary_postag
}

RDR_PATH = {
    'eng': "UD_English-EWT/en_ewt-ud-train.conllu"
}

STANZA_LANGUAGE_MAP = {
    'eng': 'en'
}

STANZA_VOCAB ={
    'upos': glossary_universal,
    'xpos': glossary_postag,
    'dep': glossary_arguments
}

SPACY_LANGUAGE_MAP = {
    'eng': 'en_core_web_sm'
}

SPECIAL_SPTOKENS = {'##': 'post', 'Ġ': 'pre'}

SPACY_VOCAB ={
    'upos': glossary_universal,
    'xpos': glossary_postag
}


def rdr_parser(parser, sentence: str, tokens: list, lang: str, **kwargs) -> Union[Tuple[dict, list], dict, None]:
    upos_dict_path = Path(__file__).parent.parent / os.path.join("tools", "parsers", "RDRPOSTagger", "Models", "ud-treebanks-v2.4", f'{RDR_PATH[lang]}.UPOS.DICT')
    xpos_dict_path = Path(__file__).parent.parent / os.path.join("tools", "parsers", "RDRPOSTagger", "Models", "ud-treebanks-v2.4", f"{RDR_PATH[lang]}.XPOS.DICT")
    upos_rdr_path = Path(__file__).parent.parent / os.path.join("tools", "parsers", "RDRPOSTagger", "Models", "ud-treebanks-v2.4", f"{RDR_PATH[lang]}.UPOS.RDR")
    xpos_rdr_path = Path(__file__).parent.parent / os.path.join("tools", "parsers", "RDRPOSTagger", "Models", "ud-treebanks-v2.4", f"{RDR_PATH[lang]}.XPOS.RDR")
    
    upos_dict = readDictionary(upos_dict_path)
    xpos_dict = readDictionary(xpos_dict_path)
    
    upos, xpos, dep = False, False, False
    res = {}
    if 'upos' in kwargs and kwargs['upos']:
        upos = True
        res['upos'] = []
    if 'xpos' in kwargs and kwargs['xpos']:
        xpos = True
        res['xpos'] = []
    if 'dep' in kwargs and kwargs['dep']:
        dep = True
        res['dep'] = []
    if not (upos or xpos or dep): return None
    # Parse
    parser_tokens = []
    
    # TODO: rdrpos using split() to tokenize a sentence, may need better solution
    def format_input(sentence: str) -> str:
        format_sentence = ""
        
        for i,c in enumerate(sentence):
            if _is_punctuation(c):
                if sentence[i-1] != ' ':
                    format_sentence += ' '
                format_sentence += c
                if i+1 < len(sentence) and sentence[i+1] != ' ':
                    format_sentence += ' '
            else:
                format_sentence += c
        return format_sentence
    
    format_sentence = format_input(sentence)  
    words = format_sentence.split()
    
    # upos
    parser.constructSCRDRtreeFromRDRfile(upos_rdr_path)
    upos_res = parser.tagRawSentence(DICT=upos_dict, rawLine = format_sentence)
    
    # xpos
    parser.constructSCRDRtreeFromRDRfile(xpos_rdr_path)
    xpos_res = parser.tagRawSentence(DICT=xpos_dict, rawLine = format_sentence)
    
    for w, u, x in zip(words, upos_res, xpos_res):
        parser_tokens.append(w)
        if upos: res['upos'].append("<{}>".format(u))
        if xpos: res['xpos'].append("<{}>".format(x))
    # Align tokens
    token_mapper = align_tokens_and_parsers(parser_tokens, tokens)
    # Pad elements
    for i in range(len(parser_tokens) - 1, -1, -1):
        if isinstance(token_mapper[i], list):
            for _ in range(token_mapper[i][0], token_mapper[i][1]):
                if upos: res['upos'].insert(i, res['upos'][i])
                if xpos: res['xpos'].insert(i, res['xpos'][i])
    if 'need_mask' in kwargs and kwargs['need_mask']:
        mask = []
        for key in token_mapper:
            if isinstance(token_mapper[key], list): mask.append(token_mapper[key])
        return res, mask
    return res


def rdr_parser_batch(parser, sentences: List[str], batch_tokens: List[list], lang: str, **kwargs) -> Union[list, None]:
    batch_res = []
    for tokens, sentence in zip(batch_tokens,sentences):
        batch_res.append(rdr_parser(parser, sentence, tokens, lang, **kwargs))
    return batch_res


def rdr_initializer(lang: str, logger: Logger) :
    if not RDR_AVAILABLE:
        logger.error("It looks like you haven't installed the RDRPOSTagger library yet. Please install it from https://github.com/datquocnguyen/RDRPOSTagger.")
        raise Exception("It looks like you haven't installed the RDRPOSTagger library yet. Please install it from https://github.com/datquocnguyen/RDRPOSTagger.")
    if lang not in RDR_LANGUAGE_MAP:
        logger.error("The language `{}` you need doesn't to be contained in `RDR_LANGUAGE_MAP`. Please check.".format(lang))
        raise Exception("The language `{}` you need doesn't to be contained in `RDR_LANGUAGE_MAP`. Please check.".format(lang))
    try:
        RDR_handler = RDRPOSTagger()
        return RDR_handler
    except:
        import traceback
        logger.error(traceback.print_exc())
        print(traceback.print_exc())


def stanza_parser(parser, sentence: str, tokens: list, lang: str, **kwargs) -> Union[Tuple[dict, list], dict, None]:
    # Parse arguments
    res = {}
    upos, xpos, dep = False, False, False
    if 'upos' in kwargs and kwargs['upos']:
        upos = True
        res['upos'] = []
    if 'xpos' in kwargs and kwargs['xpos']:
        xpos = True
        res['xpos'] = []
    if 'dep' in kwargs and kwargs['dep']:
        dep = True
        res['dep'] = []
    if not (upos or xpos or dep): return None
    
    # Parse
    parser_tokens = []
    doc = parser(sentence)
    
    doc = doc.sentences[0]
    
    parser_tokens = []
    for token in doc.words:
        text = token.text
        parser_tokens.append(text)
        uni = token.upos
        pos = token.xpos
        deprel = token.deprel
        if upos: res['upos'].append("<{}>".format(uni))
        if xpos: res['xpos'].append("<{}>".format(pos))
        if dep: res['dep'].append("<{}>".format(deprel))

    token_mapper = align_tokens_and_parsers(parser_tokens, tokens)
    
    for i in range(len(parser_tokens) -1, -1, -1):
        if isinstance(token_mapper[i], list):
            for _ in range(token_mapper[i][0], token_mapper[i][1]):
                if upos: res['upos'].insert(i, res['upos'][i])
                if xpos: res['xpos'].insert(i, res['xpos'][i])
                if dep: res['dep'].insert(i, res['dep'][i])
    if 'need_mask' in kwargs and kwargs['need_mask']:
        mask = []
        for key in token_mapper:
            if isinstance(token_mapper[key], list): mask.append(token_mapper[key])
        return res, mask
    return res


def stanza_parser_batch(parser, sentences: Union[list, str], batch_tokens: List[list], lang: str, **kwargs) -> Union[list, None]:
    if isinstance(sentences, str):
        sentences = [sentences]
        tokens = [batch_tokens]
    
    # Parse arguments
    upos, xpos, dep = False, False, False
    batch_res = []
    if 'upos' in kwargs and kwargs['upos']:
        upos = True
    if 'xpos' in kwargs and kwargs['xpos']:
        xpos = True
    if 'dep' in kwargs and kwargs['dep']:
        dep = True
    if not (upos or xpos or dep): return None
    # Parse
    parser_tokens = []
    in_docs = [Document([], text = d) for d in sentences]    
    out_docs = parser(in_docs)
    
    if isinstance(out_docs, Document):
        out_docs = [out_docs]
    
    for tokens, doc in zip(batch_tokens, out_docs):
        res = {}
        if upos:
            res['upos'] = []
        if xpos:
            res['xpos'] = []
        if dep:
            res['dep'] = []

        doc = doc.sentences[0]
        
        parser_tokens = []
        for token in doc.words:
            text = token.text
            parser_tokens.append(text)
            uni = token.upos
            pos = token.xpos
            deprel = token.deprel
            if upos: res['upos'].append("<{}>".format(uni))
            if xpos: res['xpos'].append("<{}>".format(pos))
            if dep: res['dep'].append("<{}>".format(deprel))

        token_mapper = align_tokens_and_parsers(parser_tokens, tokens)
        
        for i in range(len(parser_tokens) -1, -1, -1):
            if isinstance(token_mapper[i], list):
                for _ in range(token_mapper[i][0], token_mapper[i][1]):
                    if upos: res['upos'].insert(i, res['upos'][i])
                    if xpos: res['xpos'].insert(i, res['xpos'][i])
                    if dep: res['dep'].insert(i, res['dep'][i])
        
        batch_res.append(res)

    return batch_res


def stanza_initializer(lang:str, logger: Logger):
    if not STANZA_AVAILABLE:
        logger.error("It looks like you haven't installed the stanza library yet. Please install it first using `pip install stanza`.")
        raise Exception("It looks like you haven't installed the stanza library yet. Please install it first using `pip install stanza`.")
    if lang not in STANZA_LANGUAGE_MAP:
        logger.error("The language `{}` you need doesn't to be contained in `STANZA_LANGUAGE_MAP`. Please check.".format(lang))
        raise Exception("The language `{}` you need doesn't to be contained in `STANZA_LANGUAGE_MAP`. Please check.".format(lang))
    try:
        stanza_handler = stanza.Pipeline(STANZA_LANGUAGE_MAP[lang],
                                         processors='tokenize, mwt, pos, lemma, depparse', 
                                         tokenize_no_ssplit = True,
                                         )
        return stanza_handler
    except:
        import traceback
        logger.error(traceback.print_exc())
        print(traceback.print_exc())


def spacy_parser(parser, sentence: list, tokens: list, lang: str, **kwargs) -> Union[Tuple[dict, list], dict, None]:
    # TODO: Add mask part for other parsers (2023/7/3)
    # Parse arguments
    upos, xpos, dep = False, False, False
    res = {}
    if 'upos' in kwargs and kwargs['upos']:
        upos = True
        res['upos'] = []
    if 'xpos' in kwargs and kwargs['xpos']:
        xpos = True
        res['xpos'] = []
    if 'dep' in kwargs and kwargs['dep']:
        dep = True
        res['dep'] = []
    if not (upos or xpos or dep): return None
    # Parse
    parser_tokens = []
    doc = parser(sentence)
    for index, tok in enumerate(doc):
        text = tok.text
        parser_tokens.append(text)
        uni = tok.pos_
        pos = tok.tag_
        if upos: res['upos'].append("<{}>".format(uni))
        if xpos: res['xpos'].append("<{}>".format(pos))
    # Align tokens
    token_mapper = align_tokens_and_parsers(parser_tokens, tokens)
    if token_mapper is None: return None
    tabu_list = []
    # Pad elements
    for i in range(len(parser_tokens) - 1, -1, -1):
        if token_mapper[i] in tabu_list:
            if upos: del res['upos'][i]
            if xpos: del res['xpos'][i]
        if isinstance(token_mapper[i], list):
            for _ in range(token_mapper[i][0], token_mapper[i][1]):
                if upos: res['upos'].insert(i, res['upos'][i])
                if xpos: res['xpos'].insert(i, res['xpos'][i])
        else: tabu_list.append(token_mapper[i])
    if 'need_mask' in kwargs and kwargs['need_mask']:
        mask = []
        for key in token_mapper:
            if isinstance(token_mapper[key], list): mask.append(token_mapper[key])
        return res, mask
    return res


def spacy_parser_batch(parser, sentences: List[str], batch_tokens: List[list], lang: str, **kwargs) -> Any:
    if isinstance(sentences, str):
        sentences = [sentences]
        batch_tokens = [batch_tokens]
        
    upos, xpos, dep = False, False, False
    if 'upos' in kwargs and kwargs['upos']:
        upos = True
    if 'xpos' in kwargs and kwargs['xpos']:
        xpos = True
    if 'dep' in kwargs and kwargs['dep']:
        dep = True
    if not (upos or xpos or dep): return None
    
    batch_res, batch_mask = [], []
    # Parse
    docs = parser.pipe(sentences, n_process=1)
    for tokens, doc in zip(batch_tokens, docs):
        res = {}
        if upos: res['upos'] = []
        if xpos: res['xpos'] = []
        if dep: res['dep'] = []
        parser_tokens = []  
        for index, tok in enumerate(doc):
            text = tok.text
            parser_tokens.append(text)
            uni = tok.pos_
            pos = tok.tag_
            if upos: res['upos'].append("<{}>".format(uni))
            if xpos: res['xpos'].append("<{}>".format(pos))
        # Align tokens
        token_mapper = align_tokens_and_parsers(parser_tokens, tokens)
        # Align tokens
        token_mapper = align_tokens_and_parsers(parser_tokens, tokens)
        tabu_list = []
        # Pad elements
        for i in range(len(parser_tokens) - 1, -1, -1):
            if token_mapper[i] in tabu_list:
                if upos: del res['upos'][i]
                if xpos: del res['xpos'][i]
            if isinstance(token_mapper[i], list):
                for _ in range(token_mapper[i][0], token_mapper[i][1]):
                    if upos: res['upos'].insert(i, res['upos'][i])
                    if xpos: res['xpos'].insert(i, res['xpos'][i])
            else:
                tabu_list.append(token_mapper[i])
        batch_res.append(res)
        if 'need_mask' in kwargs and kwargs['need_mask']:
            mask = []
            for key in token_mapper:
                if isinstance(token_mapper[key], list): mask.append(token_mapper[key])
            batch_mask.append(mask)
    if 'need_mask' in kwargs and kwargs['need_mask']:
        return batch_res, batch_mask
    else:
        return batch_res


def spacy_initializer(lang: str, logger: Logger):
    if not SPACY_AVAILABLE:
        logger.error("It looks like you haven't installed the spaCy library yet. Please install it first using `pip install spacy`.")
        raise Exception("It looks like you haven't installed the spaCy library yet. Please install it first using `pip install spacy`.")
    if lang not in SPACY_LANGUAGE_MAP:
        logger.error("The language `{}` you need doesn't to be contained in `SPACY_LANGUAGE_MAP`. Please check.".format(lang))
        raise Exception("The language `{}` you need doesn't to be contained in `SPACY_LANGUAGE_MAP`. Please check.".format(lang))
    try:
        spacy_handler = spacy.load(SPACY_LANGUAGE_MAP[lang])
        spacy_handler.disable_pipes(['ner', 'parser', 'lemmatizer'])
        return spacy_handler
    except:
        import traceback
        logger.error(traceback.print_exc())
        print(traceback.print_exc())


def align_tokens_and_parsers(token_parser: list, token_tokenizer: list, watch_dog : int = 0) -> Union[dict, None]:
    index_map = {}
    tpi, ttib, ttie, collect_tok, collect_par = 0, 0, 0, "", ""
    tempo_tti = 0
    # Watch dog for error tracing
    if watch_dog > len(token_tokenizer):
        return None

    def _det_sptoken(tokens: list) -> Union[str, None]:
        for tok in tokens:
            for sptok in SPECIAL_SPTOKENS:
                if sptok in tok: return sptok
        return None

    def _update_equal_index(index: int) -> None:
        if ttie - ttib == index - tpi:
            index_map.update({tpi + _: ttib + _ for _ in range(ttie - ttib + 1)})
        else:
            union = min(ttie - ttib, index - tpi)
            index_map.update({tpi + _: ttib + _ for _ in range(union)})
            index_map.update({_: ttib + union if ttib + union == ttie else [ttib + union, ttie] for _ in
                              range(tpi + union, index + 1)})

    def _try_repair_tokens(st_paridx: int, st_tokidx: int) -> Union[str, None]:
        # TODO: Some complex case should be taken into consideration.
        error_st, error_ed, refer_st, refer_ed = st_tokidx + 1, -1, st_paridx + 1, -1
        error_flag = False
        for i in range(error_st + 1, len(token_tokenizer)):
            tok = token_tokenizer[i].replace(sptok, '').lower()
            find_refer = [tp + refer_st for tp, tptok in enumerate(token_parser[refer_st:]) if tptok.startswith(tok) or tok.startswith(tptok)]
            if len(find_refer) > 0:
                error_flag = True
                error_ed, refer_ed = i, find_refer[0]
                break
        if error_flag:
            if error_ed - error_st == refer_ed - refer_st:
                for idx in range(0, error_ed - error_st): token_tokenizer[idx + error_st] = token_parser[idx + refer_st]
            elif error_ed - error_st > refer_ed - refer_st:
                for idx in range(0, refer_ed - refer_st): token_tokenizer[idx + error_st] = token_parser[idx + refer_st]
                for idx in range(refer_ed - refer_st, error_ed - error_st): token_tokenizer[idx + error_st] = ''
            else:
                return None
            return align_tokens_and_parsers(token_parser, token_tokenizer, watch_dog+1)
        else:
            return None

    # determine the special token
    sptok = _det_sptoken(token_tokenizer)
    if sptok is None:
        # return {i: i for i in range(len(token_parser))} # Find bugs
        sptok = ""
    # mapping
    for i, tokpar in enumerate(token_parser):
        collect_par += tokpar.lower()
        if len(collect_tok) == len(collect_par) and collect_tok == collect_par:
            _update_equal_index(i)
            tpi = i + 1
            ttib = ttie + 1
            tempo_tti = ttib
            collect_par, collect_tok = "", ""
        else:
            if len(collect_tok) < len(collect_par):
                for ti in range(tempo_tti, len(token_tokenizer)):
                    collect_tok += token_tokenizer[ti].replace(sptok, '').lower()
                    ttie = ti
                    if len(collect_tok) >= len(collect_par): break
                if len(collect_tok) == len(collect_par) and collect_tok == collect_par:
                    _update_equal_index(i)
                    tpi = i + 1
                    ttib = ttie + 1
                    tempo_tti = ttib
                    collect_par, collect_tok = "", ""
                    continue
                tempo_tti = ttie + 1
            else:
                continue
    # trace error
    if len(index_map) == 0 or len(index_map.keys()) != len(token_parser):
        if len(index_map) == 0: st_paridx, st_tokidx = -1, -1
        else:
            st_paridx, st_tokidx = list(index_map.keys())[-1], list(index_map.values())[-1][-1] if isinstance(
                list(index_map.values())[-1], list) else list(index_map.values())[-1]
        return _try_repair_tokens(st_paridx, st_tokidx)
    return index_map


def flatten_results(results: dict, parser_weight: dict, level_name: str, length: int = None) -> list:
    parser_list = list(results.keys())
    if len(parser_list) == 1: return results[parser_list[0]]
    parse_result = []
    if length is None: length = len(results[parser_list[0]])
    for i in range(length):
        element_dict = OrderedDict()
        for p in parser_list:
            if results[p][i] in element_dict: element_dict[results[p][i]] += parser_weight[p][-1][level_name]
            else: element_dict[results[p][i]] = parser_weight[p][-1][level_name]
        argmax_ids = np.argmax(element_dict.values())
        parse_result.append(list(element_dict.keys())[argmax_ids])
    return parse_result


def _is_control(char):
    """Checks whether `chars` is a control character."""
    # These are technically control characters but we count them as whitespace
    # characters.
    if char == "\t" or char == "\n" or char == "\r":
        return False
    cat = unicodedata.category(char)
    if cat in ("Cc", "Cf"):
        return True
    return False


def _is_punctuation(char):
    """Checks whether `chars` is a punctuation character."""
    cp = ord(char)
    # We treat all non-letter/number ASCII as punctuation.
    # Characters such as "^", "$", and "`" are not in the Unicode
    # Punctuation class but we treat them as punctuation anyways, for
    # consistency.
    if ((cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or
            (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126)):
        return True
    cat = unicodedata.category(char)
    if cat.startswith("P"):
        return True
    return False


def is_parser_legal(parser_content: list) -> bool:
    if len(parser_content) != 2 or parser_content[-1] is None: return False
    else: return True


def convert_tokens_to_str(tokens: Union[str, List[str]]) -> str:
    if isinstance(tokens, str):
        for sp in SPECIAL_SPTOKENS: tokens = tokens.replace(sp, '')
        return tokens
    return_tokens = ' '.join(tokens)
    for sp in SPECIAL_SPTOKENS:
        if sp in return_tokens:
            if SPECIAL_SPTOKENS[sp] == 'pre':
                return_tokens = ''.join(tokens)
                return_tokens = return_tokens.replace(sp, ' ')
            else:
                # Pre case
                return_tokens = ' '.join(tokens)
                return_tokens = return_tokens.replace(sp, '')
    return return_tokens


def encode_lexical_stoken(lexical: List[str], tokenizer, special_token: str = "Ġ") -> List[str]:
    if special_token + lexical[0] in tokenizer.vocab:
        lexical[0] = special_token + lexical[0]
    return lexical


class DefaultParser:
    # Format [Initialize (Optional[None], Parser, Vocab)
    SPACY = [spacy_initializer, spacy_parser, spacy_parser_batch, SPACY_VOCAB]
    STANZA = [stanza_initializer, stanza_parser, stanza_parser_batch, STANZA_VOCAB]
    RDRPOS = [rdr_initializer, rdr_parser, rdr_parser_batch, RDR_VOCAB]
    DEFAULT_AFFIX = []


default_parsers = {
    'spaCy': DefaultParser.SPACY,
    'stanza': DefaultParser.STANZA,
    'rdrpos': DefaultParser.RDRPOS,
    'default_affix': DefaultParser.DEFAULT_AFFIX
}
