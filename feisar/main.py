from pathlib import Path
import os
import typer

from feisar.engine import create_engine
from feisar.session import Session
from feisar.schema import CodeFile
from feisar.search import Search

app = typer.Typer()


engine = create_engine("xapian://dbx")


def python_files_iter(folder: str):
    for root, dirs, files in os.walk(folder):
        filtered_files = [file for file in files if file.endswith('py')]
        if len(filtered_files):
            for file in files:
                yield Path(root) / Path(file)


@app.command()
def index(folder: str):
    session = Session(engine)
    doc_id = 0

    for path in python_files_iter(folder):
        with open(path, 'r') as f:
            text = f.read()

        doc_id += 1
        code_file = CodeFile(id=doc_id, text=text, path=str(path))
        session.add(code_file)


@app.command()
def search(querystring: str, offset:int = 0, pagesize:int = 10):
    session = Session(engine)
    sq = Search(CodeFile).query(querystring)

    for code_file in session.exec(sq):
        print(code_file)
