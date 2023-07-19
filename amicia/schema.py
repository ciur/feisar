from amicia.field import Field
from amicia.index import SearchIndex


class CodeFile(SearchIndex):
    id: int = Field(primary_key=True)
    path: str
    text: str
