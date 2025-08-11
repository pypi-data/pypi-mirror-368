# Description: Schema Document
from dataclasses import dataclass

from scaledp.schemas.Box import Box
from scaledp.utils.dataclass import map_dataclass_to_struct, register_type


@dataclass(order=True)
class Document:
    path: str
    text: str
    type: str
    bboxes: list[Box]
    exception: str = ""

    @staticmethod
    def get_schema():
        return map_dataclass_to_struct(Document)


register_type(Document, Document.get_schema)
