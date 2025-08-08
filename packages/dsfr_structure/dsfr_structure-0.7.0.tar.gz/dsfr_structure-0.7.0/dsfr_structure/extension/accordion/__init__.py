from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_boolean
import xml.etree.ElementTree as etree


class DsfrAccordion(Block):
    NAME = "accordion"
    ARGUMENT = True
    OPTIONS = {
        "open": (False, type_boolean),
    }

    count = 0

    def on_create(self, parent):
        # <section class="fr-accordion">
        # <h5 class="fr-accordion__title">
        # <button class="fr-accordion__btn" aria-expanded="false" aria-controls="accordion-106">
        # Intitulé accordéon
        # </button>
        # </h5>
        # <div class="fr-collapse" id="accordion-106">
        #         <!-- données de test -->
        # </div>
        # </section>
        accordion_id = "accordion-%s" % DsfrAccordion.count
        DsfrAccordion.count += 1

        if self.options["open"]:
            is_open = "true"
        else:
            is_open = "false"
        section = etree.SubElement(parent, "section")
        section.set("class", "fr-accordion")

        h5 = etree.SubElement(section, "h5")
        h5.set("class", "fr-accordion__title")

        button = etree.SubElement(h5, "button")
        button.set("class", "fr-accordion__btn")
        button.set("aria-expanded", is_open)
        button.set("aria-controls", accordion_id)

        button.text = self.argument

        content = etree.SubElement(section, "div")
        if self.options["open"]:
            content.set("class", "fr-collapse fr-collapse--open")
        else:
            content.set("class", "fr-collapse")
        content.set("id", accordion_id)

        return content


class DsfrAccordionExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrAccordion, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrAccordionExtension(*args, **kwargs)
