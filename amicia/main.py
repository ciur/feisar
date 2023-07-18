from pathlib import Path
import os
import json

import typer
import xapian

app = typer.Typer()


def python_files_iter(folder: str):
    for root, dirs, files in os.walk(folder):
        filtered_files = [file for file in files if file.endswith('py')]
        if len(filtered_files):
            for file in files:
                yield Path(root) / Path(file)


@app.command()
def index(folder: str, dbpath: str):
    db = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)

    termgen = xapian.TermGenerator()
    termgen.set_stemmer(xapian.Stem('en'))

    doc_id = 0
    for path in python_files_iter(folder):
        doc_id += 1
        with open(path, 'r') as f:
            text = f.read()
        doc = xapian.Document()

        termgen.set_document(doc)
        termgen.index_text(text, 1, 'XD')  # text
        termgen.index_text(str(path), 1, 'S')  # path

        termgen.index_text(text)
        termgen.increase_termpos()
        termgen.index_text(str(path))

        # Store all the fields for display purposes.
        doc.set_data(json.dumps({'path': str(path)}))

        id_term = f'doc_id_{doc_id}'
        doc.add_boolean_term(id_term)
        db.replace_document(id_term, doc)


@app.command()
def search(dbpath: str, querystring: str, offset:int = 0, pagesize:int = 10):
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

