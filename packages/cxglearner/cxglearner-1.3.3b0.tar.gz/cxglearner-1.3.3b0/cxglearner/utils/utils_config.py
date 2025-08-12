import os
import json
from ..config.config_check import *
from typing import Optional, Union


class DefaultConfigs:
    eng: str = os.path.abspath(os.path.join(os.path.dirname(
        __file__), "../resources/configs/eng/eng_config.json"))


class DefaultModelConfigs:
    GPT_Base: str = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../resources/models/GPT_Base/"))
    GPT_Medium: str = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../resources/models/GPT_Medium/"))
    GPT_Small: str = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../resources/models/GPT_Small/"))


def load_hyperparam(default_args) -> None:
    """
    Load arguments form argparse and config file
    Priority: default options < config file
    """
    assert os.path.exists(os.path.join(default_args.config_path, 'config.json')), "Cannot find model config file '{}', please check.".format(
        os.path.join(default_args.config_path, 'config.json'))
    with open(os.path.join(default_args.config_path, 'config.json'), mode="r", encoding="utf-8") as f:
        config_args_dict = json.load(f)
    default_args.__dict__.update(config_args_dict)


def load_customparams(config_path: str) -> dict:
    """
    Load customized arguments form config file.
    """
    assert os.path.exists(
        config_path), "Cannot find custom config file '{}', please check.".format(config_path)
    with open(config_path, mode="r", encoding="utf-8") as f:
        config_args_dict = json.load(f)
    return config_args_dict


def convert_json2object(key_or_dict: Union[str, dict]) -> Union[str, dict, None]:
    """
    Convert key name of json file to Config type.
    """
    if isinstance(key_or_dict, str):
        return ''.join(['_{}'.format(_.lower()) if not _.islower() and _ != "_" else _ for _ in key_or_dict])
    elif isinstance(key_or_dict, dict):
        new_dict = dict()
        for key in key_or_dict:
            new_dict[''.join(['_{}'.format(_.lower()) if not _.islower(
            ) else _ for _ in key])] = key_or_dict[key]
        return new_dict
    else:
        return None


def argument_check_and_merge(args: dict, config) -> None:
    """
    Check the validity of arguments and filter out the illegal args.
    """
    filtered_args, nessesitys, check_map, illegal_prompts = {}, [], {}, []
    # Recur parsing

    def _get_argpairs(inner_args: Union[dict, str], module_name: Optional[str] = None):
        parsed_args = {}
        key_prefix = "" if not module_name else module_name + "_"
        for key in inner_args:
            if isinstance(inner_args[key], dict) and key not in LEGAL_PAR:
                parsed_args.update(_get_argpairs(inner_args[key]))
            else:
                if isinstance(inner_args[key], dict):
                    inner_args_trans = convert_json2object(inner_args[key])
                    parsed_args[key_prefix+key] = inner_args_trans
                else:
                    parsed_args[key_prefix +
                                convert_json2object(key)] = inner_args[key]
        return parsed_args
    # Re-organize arguments
    for con in CONFIG_CHECK:
        if CONFIG_CHECK[con][-1]:
            nessesitys.append(CONFIG_CHECK[con][0][-1])
        check_map[CONFIG_CHECK[con][0][0] +
                  '_' + CONFIG_CHECK[con][0][-1]] = con
    # Filter arguments
    legal_modules = [key[:-1] for key in CONFIG_MAP.keys()]
    for module in args:
        if module not in legal_modules:
            illegal_prompts.append(
                'Module {} is not contained in config class.'.format(module))
        module_args = args[module]
        for arg in module_args:
            NESSES = False
            if arg in nessesitys:
                nessesitys.remove(arg)
                NESSES = True
            if module + '_' + arg not in check_map:
                illegal_prompts.append(
                    'Argument `{}.{} is not exists, please check the document.'.format(module, arg))
                continue
            if not isinstance(module_args[arg], dict):
                if isinstance(module_args[arg], CONFIG_CHECK[check_map[module + '_' + arg]][-2]):
                    filtered_args[module + '_' + arg] = module_args[arg]
                else:
                    illegal_prompts.append('Argument `{}.{} has illegal type `{}`, rather than `{}`.'.format(
                        module, arg, type(module_args[arg]), CONFIG_CHECK[check_map[module + '_' + arg]][-2]))
                    assert not NESSES, "Argument `{}` is mandatory, but has not passed the format check.".format(
                        arg)
            else:
                if arg in LEGAL_PAR:
                    filtered_args[module + '_' +
                                  arg] = convert_json2object(module_args[arg])
                else:
                    inner_args = _get_argpairs(module_args[arg])
                    for iarg in inner_args:
                        ciarg = convert_json2object(iarg)
                        if ciarg in config.__dict__[module].__dict__:
                            check_map[module + '_' +
                                      iarg] = module + '_' + ciarg
                            filtered_args[module + '_' +
                                          iarg] = inner_args[iarg]
                        else:
                            illegal_prompts.append(
                                'Argument `{}.{}.{} is not exists, please check the document.'.format(module, arg, iarg))
    # Check necessary arguments
    if len(nessesitys) > 0:
        print('>> Argument Error:')
        for ness in nessesitys:
            print(
                "Argument `{}` is mandatory, but not exists in the config file.".format(ness))
        raise Exception(
            'You can browse the document to check for the above arguments.')
    # Assign arguments
    for arg in filtered_args:
        module, carg = check_map[arg].split('_', 1)
        config.__dict__[CONFIG_MAP[module+'_']
                        ].__dict__[carg] = filtered_args[arg]
    # Output Illegal
    if len(illegal_prompts) > 0:
        print('>> Illegal Arguments:')
        for ill in illegal_prompts:
            print(ill)
        print("The above arguments will be ignored. If any crucial parameters are ignored, you can stop the execution.")
