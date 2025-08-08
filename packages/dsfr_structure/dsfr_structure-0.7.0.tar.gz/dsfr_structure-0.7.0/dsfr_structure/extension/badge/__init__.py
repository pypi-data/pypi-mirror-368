from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_string_in, type_boolean, type_string
import xml.etree.ElementTree as etree


class DsfrBadge(Block):
    NAME = "badge"
    ARGUMENT = False
    OPTIONS = {
        "type": ("", type_string_in(["", "success", "error", "info", "warning", "new"])),
        "icon": (True, type_boolean),
        "color": ("", type_string)
    }

    def on_create(self, parent):
        # <p class="fr-badge fr-badge--success fr-badge--no-icon">Label badge</p>
        # ou
        # <p class="fr-badge fr-badge--green-menthe">Label badge</p>

        badge_p = etree.SubElement(parent, "p")

        if self.options["type"]:
            if self.options["icon"]:
                badge_p.set("class", f"fr-badge fr-badge--{self.options['type']}")
            else:
                badge_p.set("class", f"fr-badge fr-badge--{self.options['type']} fr-badge--no-icon")
        elif self.options["color"]:
            badge_p.set("class", f"fr-badge fr-badge--{self.options['color']}")
        else:
            badge_p.set("class", "fr-badge")

        return badge_p


class DsfrBadgeExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrBadge, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrBadgeExtension(*args, **kwargs)
