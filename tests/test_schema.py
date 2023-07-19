from feisar.field import Field
from feisar.index import SearchIndex


class CodeFile(SearchIndex):
    id: int = Field(primary_key=True)
    path: str
    text: str


def test_basic_schema():
    code_file = CodeFile(id=1, path="/some/path", text="some-text")
    assert code_file
