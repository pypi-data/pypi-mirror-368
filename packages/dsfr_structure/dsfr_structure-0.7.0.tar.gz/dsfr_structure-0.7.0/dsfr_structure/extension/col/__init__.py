import xml.etree.ElementTree as etree

from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_string


class DsfrCol(Block):
    NAME = "col"
    ARGUMENT = None
    OPTIONS = {
        "class": ("", type_string),
    }

    def on_create(self, parent):
        # <div class="fr-col-{argument[0]} fr-col-{argument[1]} {class}">
        #     ...
        # </div>

        extra_classes = ""
        if self.options["class"]:
            extra_classes = self.options["class"]
        if self.argument:
            class_list = " ".join([f'fr-col-{arg}' for arg in self.argument.split(" ")])
        else:
            class_list = "fr-col"
        col_div = etree.SubElement(parent, "div")
        col_div.set("class", f"{class_list} {extra_classes}")

        return col_div


class DsfrColExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrCol, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrColExtension(*args, **kwargs)
