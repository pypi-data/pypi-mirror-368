from typing import Union, Optional, List, Any
from .predefine import CXS_LINK_SYMBOL
from .utils_extractor import flatten_slots
from logging import Logger


def convert_slots_to_str(slots: Union[List, List[List]], encoder: Optional[Any] = None, logger: Optional[Logger] = None,
                         link_symbol: Optional[str] = CXS_LINK_SYMBOL) -> Union[str, List[str], List[List[str]]]:
    if len(slots) > 0:
        if not isinstance(slots[0], list):
            slots = [slots]
        if len(slots[0]) > 0 and isinstance(slots[0], str):
            is_ids = False
        else:
            is_ids = True
    else:
        return []
    if is_ids and encoder is not None:
        slots = [encoder.convert_ids_to_tokens(
            flatten_slots(sl)) for sl in slots]
    else:
        err_msg = "The `slots` appear to be index, but the `encoder` is None, so it cannot be decoded to tokens."
        if logger is not None:
            logger.error(err_msg)
        raise AttributeError(err_msg)
    slots = [link_symbol.join(sl) for sl in slots]
    if len(slots) == 1:
        slots = slots[0]
    return slots
