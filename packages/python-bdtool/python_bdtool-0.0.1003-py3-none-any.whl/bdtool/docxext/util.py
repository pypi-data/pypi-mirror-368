from __future__ import annotations
import docx
from docx.opc.constants import RELATIONSHIP_TYPE as RT


def remove_existing_style_relationship(doc, part=RT.STYLES):
    rels = doc.part.rels
    style_rel_ids = [
        rel_id for rel_id, rel in rels.items()
        if rel.reltype == part
    ]

    for rel_id in style_rel_ids:
        del rels[rel_id]


def use_template(template_file):
    template = docx.Document(template_file)
    document = docx.Document()
    remove_existing_style_relationship(document, RT.STYLES)
    remove_existing_style_relationship(document, RT.NUMBERING)
    document._part.relate_to(template._part.numbering_part, RT.NUMBERING)
    document._part.relate_to(template._part._styles_part, RT.STYLES)
    return document


