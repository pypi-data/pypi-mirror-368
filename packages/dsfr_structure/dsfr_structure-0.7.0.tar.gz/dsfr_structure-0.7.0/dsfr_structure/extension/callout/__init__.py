from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_boolean, type_string_in,type_string
import xml.etree.ElementTree as etree


class DsfrCallout(Block):
    NAME = "callout"
    ARGUMENT = None
    OPTIONS = {
        "color": ("", type_string),
        "markup": ("p", type_string_in(["p","h1","h2","h3","h4","h5","h6"])),
        "icon" : ("", type_string),
        "link_label": ("", type_string),
        "link_url": ("", type_string),
        "link_newtab": (False, type_boolean),
    }

    count = 0

    def on_create(self, parent):
        # <div id="1" class="fr-callout fr-icon-info-line fr-callout--purple-glycine">
        #   <h3 class="fr-callout__title">Titre de la mise en avant</h3>
        #   <p class="fr-callout__text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam nec purus nec libero ultricies aliquet</p>
        #   <button type="button" class="fr-btn">En savoir plus</button>
        # </div>

        callout_div = etree.SubElement(parent, "div")
        callout_class = "fr-callout"
        if self.options["icon"]:
            callout_class += f" fr-icon-{self.options['icon']}"
        if self.options["color"]:
            callout_class += f" fr-callout--{self.options['color']}"
        callout_div.set("class", callout_class)
        callout_div.set("id", str(DsfrCallout.count))
        DsfrCallout.count += 1
        if self.argument:
            markup = self.options["markup"]
            title = etree.SubElement(callout_div, markup)
            title.set("class", "fr-callout__title")
            title.text = self.argument
        text = etree.SubElement(callout_div, "p")
        text.set("class", "fr-callout__text")
        if self.options["link_label"]:
            button = etree.SubElement(callout_div, "a")
            button.set("class", "fr-btn")
            button.set("href", self.options["link_url"] if self.options["link_url"] else "#")
            if self.options["link_newtab"]:
                button.set("target", "_blank")
                button.set("rel", "noopener external")
            button.set("title", f'{self.options["link_label"]}{" - nouvelle fenêtre" if self.options["link_newtab"] else ""}')
            button.text = self.options["link_label"]
        return text

class DsfrCalloutExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrCallout, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrCalloutExtension(*args, **kwargs)
