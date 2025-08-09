import shutil
import os
import pytest

@pytest.fixture(autouse=True)
def temp_tsg_auth(monkeypatch):
    dir_name = "pytest_temp"
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        #we do this rather than deleting to avoid deleting something important
        raise FileExistsError(f"directory {dir_name} already exists, please remove it before running tests")
    monkeypatch.setenv("HOME",dir_name)
    yield
    shutil.rmtree(dir_name)    
