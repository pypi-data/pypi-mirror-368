import os
from mloptimizer.infrastructure.util.utils import init_logger, create_optimization_folder


def test_init_logger(tmp_path):
    # Create a temporary path for testing
    log_file = 'test.log'
    log_path = str(tmp_path)
    logger, logfile_path = init_logger(log_file, log_path)

    # Check if the logger file is created
    assert os.path.isfile(logfile_path), "Log file should be created"

    # Check if the filename is correct
    assert logfile_path == os.path.join(log_path, log_file), "Logger filename should match"


def test_create_optimization_folder(tmp_path):
    # Create a temporary path for testing
    folder_path = os.path.join(tmp_path, 'opt_folder')

    # Test creating a new folder
    returned_path = create_optimization_folder(folder_path)
    assert os.path.isdir(folder_path), "Folder should be created"
    assert returned_path == folder_path, "Returned path should match the created folder path"

    # Test creating an existing folder
    returned_path = create_optimization_folder(folder_path)
    assert returned_path == folder_path, "Returned path should match the existing folder path"
