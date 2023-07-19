from amicia.utils import get_db_path


def test_get_db_path():
    assert "some/db/path" == get_db_path("xapian://some/db/path")
    assert "/root/db/path" == get_db_path("xapian:///root/db/path")
