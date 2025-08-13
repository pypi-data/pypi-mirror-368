"""
This script attempts to instantiate all config classes with dummy/test values.
Intended as a pre-check for the main system pipeline to ensure all config classes
can be constructed without error. Adjust values as needed for your environment.
"""
from pprint import pprint
from logging import getLogger

from common.config_framework.base_config import BaseConfig


def get_all_config_subclasses():
    subclasses = set()
    work = [BaseConfig]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def precheck_all_configs_auto(show_output=True):
    logger = getLogger('config')
    configs = []
    config_classes = get_all_config_subclasses()
    logger.info("Found %d config classes to precheck.", len(config_classes))
    for cls in config_classes:
        try:
            instance = cls()
            instance.load()
            if show_output:
                pprint(f"{cls.__name__}: {instance.__dict__}")
            configs.append(instance)
        except Exception as e:

            logger.error("ERROR loading %s: %s", cls.__name__, e)
    logger.info("Auto config precheck complete.")


if __name__ == "__main__":
    precheck_all_configs_auto(show_output=False)
