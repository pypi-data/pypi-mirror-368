from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_string_in
import xml.etree.ElementTree as etree


class DsfrRow(Block):
    NAME = "row"
    ARGUMENT = None
    OPTIONS = {
        "halign": ("", type_string_in(["", "left", "right", "center"])),
        "valign": ("", type_string_in(["", "top", "middle", "bottom"])),
    }

    def on_create(self, parent):
        # <div class="fr-grid-row {argument} fr-grid-row--{halign} fr-grid-row--{valign}">
        #     ...
        # </div>
        valign = ""
        if self.options["valign"]:
            valign = f"fr-grid-row--{self.options['valign']}"

        halign = ""
        if self.options["halign"]:
            halign = f"fr-grid-row--{self.options['halign']}"

        extra_classes = ""
        if self.argument:
            extra_classes = self.argument
        row_div = etree.SubElement(parent, "div")
        row_div.set("class", f"fr-grid-row {extra_classes} {halign} {valign}")

        return row_div


class DsfrRowExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrRow, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrRowExtension(*args, **kwargs)
