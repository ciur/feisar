from pathlib import Path
from typing import Optional
import os
import json
import typer
import xapian

from amicia.engine import create_engine
from amicia.session import Session
from amicia.schema import CodeFile

app = typer.Typer()


engine = create_engine("xapian://dbx")


def older_search_impl(
    dbpath: str,
    querystring: str,
    offset: int = 0,
    pagesize: int = 10
):
    # offset - defines starting point within result set
    # pagesize - defines number of records to retrieve

    # Open the database we're going to search.
    db = xapian.Database(dbpath)

    # Set up a QueryParser with a stemmer and suitable prefixes
    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(xapian.Stem("en"))
    queryparser.set_stemming_strategy(queryparser.STEM_SOME)
    # Start of prefix configuration.
    queryparser.add_prefix("path", "S")
    queryparser.add_prefix("text", "XD")
    # End of prefix configuration.

    # And parse the query
    query = queryparser.parse_query(querystring)

    # Use an Enquire object on the database to run the query
    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    for match in enquire.get_mset(offset, pagesize):
        fields = json.loads(match.document.get_data().decode('utf8'))
        print("%(rank)i: #%(docid)3.3i %(title)s" % {
            'rank': match.rank + 1,
            'docid': match.docid,
            'title': fields.get('path', ''),
            })


def python_files_iter(folder: str):
    for root, dirs, files in os.walk(folder):
        filtered_files = [file for file in files if file.endswith('py')]
        if len(filtered_files):
            for file in files:
                yield Path(root) / Path(file)


@app.command()
def index(folder: str, dbpath: str):
    session = Session(engine)
    doc_id = 0

    for path in python_files_iter(folder):
        with open(path, 'r') as f:
            text = f.read()

        doc_id += 1
        code_file = CodeFile(id=doc_id, text=text, path=str(path))
        session.add(code_file)


@app.command()
def search(dbpath: str, querystring: str, offset:int = 0, pagesize:int = 10):
    pass
    #session = Session(engine)
    #sq = SearchQuery(CodeFile).where(path="xyz", text="abc")
    #session.search(sq)
