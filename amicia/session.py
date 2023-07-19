import json
import xapian

from amicia.field import Field


class Session:
    def __init__(self, engine, language="en"):
        self._engine = engine
        self._termgenerator = xapian.TermGenerator()
        self._termgenerator.set_stemmer(xapian.Stem(language))

    def add(self, entity):
        doc = xapian.Document()
        self._termgenerator.set_document(doc)

        primary_key_name = None

        for name, field in entity.model_fields.items():
            if field.annotation == str:
                self._termgenerator.index_text(name, 1, name)

            if isinstance(field.default, Field) and field.default.primary_key:
                primary_key_name = name

        doc.set_data(
            json.dumps(entity.model_dump())
        )

        if not primary_key_name:
            raise ValueError("No primary field defined")

        identifier = getattr(entity, primary_key_name)
        idterm = f"Q{identifier}"
        self._engine._db.replace_document(idterm, doc)
