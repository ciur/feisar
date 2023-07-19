from feisar.field import Field
from feisar.index import SearchIndex


class CodeFile(SearchIndex):
    id: int = Field(primary_key=True)
    path: str
    text: str
