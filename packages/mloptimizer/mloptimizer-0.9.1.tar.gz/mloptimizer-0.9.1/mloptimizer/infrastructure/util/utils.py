import logging
import os


def init_logger(filename='mloptimizer.log', log_path=".", debug=False):
    """
    Initializes a logger and returns it.

    Parameters
    ----------
    filename : str, optional
        The name of the log file. The default is 'mloptimizer.log'.
    log_path : str, optional
        The path of the log file. The default is ".".
    debug : bool, optional
        Activate debug level. The default is False.
    Returns
    -------
    custom_logger : logging.Logger
        The logger.
    """
    # Some logger variables
    logfile_path = os.path.join(log_path, filename)

    log_level = logging.INFO

    if debug:
        log_level = logging.DEBUG

    # Create a custom logger
    custom_logger = logging.getLogger(filename)
    custom_logger.setLevel(log_level)

    # Create logger formatter
    log_format = (
        "%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d")
    logger_formatter = logging.Formatter(log_format)

    # Create handler for the logger
    file_handler = logging.FileHandler(logfile_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logger_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.CRITICAL)
    console_handler.setFormatter(logger_formatter)

    # Add the handler to the logger
    custom_logger.addHandler(file_handler)
    custom_logger.addHandler(console_handler)

    # custom_logger.propagate = False

    # Logger configured
    custom_logger.debug("Logger configured")
    return custom_logger, logfile_path


def create_optimization_folder(folder):
    """
    Creates a folder to save the results of the optimization.

    Parameters
    ----------
    folder : str
        The path of the folder to create.

    Returns
    -------
    folder : str
        The path of the folder created.
    """
    if os.path.exists(folder):
        logging.warning("The folder {} already exists and it will be used".format(folder))
    elif os.makedirs(folder, exist_ok=True):
        logging.warning("The folder {} has been created.".format(folder))
    else:
        logging.error("The folder {} could not be created.".format(folder))
    return folder
