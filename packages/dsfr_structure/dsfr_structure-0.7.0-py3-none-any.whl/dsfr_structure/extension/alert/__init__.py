from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_string_in
import xml.etree.ElementTree as etree


class DsfrAlert(Block):
    NAME = "alert"
    ARGUMENT = None
    OPTIONS = {
        "type": ("info", type_string_in(["success", "error", "info", "warning"])),
        "markup": ("h5", type_string_in(["p", "h1", "h2", "h3", "h4", "h5", "h6"])),
    }

    def on_create(self, parent):
        # <div class="fr-alert fr-alert--success">
        #     <h5 class="fr-alert__title">Succès de l'envoi</h5>
        #     <p>Description</p>
        # </div>

        alert_div = etree.SubElement(parent, "div")

        if self.argument:
            alert_div.set("class", f"fr-alert fr-alert--{self.options['type']}")
            h5 = etree.SubElement(alert_div, self.options['markup'])
            h5.set("class", "fr-alert__title")
            h5.text = self.argument
        else:
            alert_div.set("class", f"fr-alert fr-alert--{self.options['type']} fr-alert--small")

        return alert_div


class DsfrAlertExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrAlert, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrAlertExtension(*args, **kwargs)
