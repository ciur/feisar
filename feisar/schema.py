from feisar.field import Field
from feisar.index import SearchIndex


class CodeFile(SearchIndex):
    id: int = Field(primary_key=True)
    path: str
    text: str

    def __str__(self):
        return f"CodeFile(id={self.id}, path={self.path})"
