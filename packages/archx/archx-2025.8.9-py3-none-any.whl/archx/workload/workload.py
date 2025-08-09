from collections import OrderedDict
from loguru import logger

from archx.utils import read_yaml, get_path, write_yaml


key_path = 'path'
key_configuration = 'configuration'
key_workload = 'workload'


def create_workload_dict(workload_file: str) -> OrderedDict:
    """
    Create a workload dict, path are loaded recursively.
    """
    # read in workload yaml
    workload_file_full_path = get_path(workload_file)
    workload_dict = read_yaml(workload_file_full_path)[key_workload]

    for workload in workload_dict:
        if key_path not in workload_dict[workload]:
            assert key_configuration in workload_dict[workload], logger.info(f'No configuration in workload <{workload}>.')
        else:
            # load workload from path
            new_workload_file = get_path(workload_dict[workload][key_path])
            workload_dict[workload] = create_workload_dict(new_workload_file)[workload]
    
    logger.success(f'Create workload dictionary from <{workload_file_full_path}>.')

    return workload_dict


def save_workload_dict(workload_dict: OrderedDict, save_path: str) -> None:
    """
    Save workload to a checkpoint
    """
    save_path = get_path(save_path, check_exist=False)
    workload_dict_ckpt = OrderedDict({key_workload: workload_dict})
    write_yaml(save_path, workload_dict_ckpt)
    logger.success(f'Save workload dictionary to <{save_path}>.')


def load_workload_dict(ckpt_path: str) -> OrderedDict:
    """
    Load workload from a checkpoint
    """
    full_path = get_path(ckpt_path)
    workload_dict = read_yaml(full_path)[key_workload]
    logger.success(f'Load workload dictionary from <{full_path}>.')
    return workload_dict

