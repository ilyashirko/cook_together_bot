import logging
from environs import Env


def make_logger(env: Env.read_env):
    log_name = env.str('LOG_FILENAME')

    log = logging.getLogger(log_name)
    log.setLevel(logging.INFO)

    filehandler = logging.FileHandler(log_name)
    basic_formater = logging.Formatter(
        '%(asctime)s : [%(levelname)s] : %(message)s'
    )
    filehandler.setFormatter(basic_formater)
    log.addHandler(filehandler)
    return log
