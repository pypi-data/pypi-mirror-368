from gym_cas import excel_read


def test_excel_read_without_module(mocker):
    mocker.patch("gym_cas.excel.load_workbook", new=None)
    data = None
    try:
        data = excel_read("test.xlsx", "A1:C3")
    except ImportError:
        assert True
    assert data is None


def test_excel():
    data = None
    try:
        data = excel_read("test.xlsx", "A1:C3")
    except ImportError:
        assert data is not None
    assert data == [["kol a", "kol b", "kol c"], ["række 2", 1, 2], ["række 3", "A", "B"]]

    data = None
    try:
        data = excel_read("no-file.xlsx", "A1:C3")
    except FileNotFoundError:
        assert data is None
    assert data is None

    try:
        data = excel_read("test.xlsx", "A1")
    except ImportError:
        assert data is not None
    assert data == "kol a"
