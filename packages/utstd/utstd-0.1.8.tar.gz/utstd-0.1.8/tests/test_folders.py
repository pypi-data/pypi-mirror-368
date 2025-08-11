import pytest

from utstd.folders import LabExFolder, AtFolder


@pytest.fixture
def lab01_ex02():
    return LabExFolder(
        course_code="36106",
        lab="lab01",
        exercise="ex02",
    )

@pytest.fixture
def at1():
    return AtFolder(
        course_code="36106",
        assignment="AT1",
    )

def test_lab_folder(lab01_ex02):
    assert lab01_ex02.course_code == "36106"
    assert lab01_ex02._lab == "lab01"
    assert lab01_ex02._exercise == "ex02"
    assert lab01_ex02.folder_path is None

def test_at_folder(at1):
    assert at1.course_code == "36106"
    assert at1._assignment == "AT1"
    assert at1.folder_path is None

