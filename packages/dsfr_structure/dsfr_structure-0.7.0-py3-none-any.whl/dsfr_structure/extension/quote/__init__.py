from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_string, type_string_in
import xml.etree.ElementTree as etree


class DsfrQuote(Block):
    NAME = "quote"
    ARGUMENT = None
    OPTIONS = {
        "size": ("md", type_string_in(["md", "lg", "xl"])),
        "image": ("", type_string),
        "color": ("", type_string),
    }

    count = 0

    def on_create(self, parent):
        # <figure class="fr-quote fr-quote--brown-caramel fr-quote--column">
        #   <blockquote>
        #     <p class="fr-text--md">« Lorem [...] elit ut. »</p>
        #   </blockquote>
        #   <figcaption>
        #     <p class="fr-quote__author">Auteur</p>
        #     <div class="fr-quote__image">
        #       <img class="fr-responsive-img" src="img/placeholder.1x1.png" alt="" />
        #       <!-- L’alternative de l’image (attribut alt) doit toujours être présente, sa valeur peut-être vide (image n’apportant pas de sens supplémentaire au contexte) ou non (porteuse de texte ou apportant du sens) selon votre contexte -->
        #     </div>
        #   </figcaption>
        # </figure>
        blockquote_id = "blockquote-%s" % DsfrQuote.count
        DsfrQuote.count += 1

        blockquote_figure = etree.SubElement(parent, "figure")
        blockquote_class = "fr-quote fr-quote--column"
        if self.options["color"]:
            blockquote_class += f" fr-quote--{self.options['color']}"
        blockquote_figure.set("class", blockquote_class)
        blockquote_figure.set("id", blockquote_id)

        blockquote_text = etree.SubElement(blockquote_figure, "blockquote")
        blockquote_content = etree.SubElement(blockquote_text, "p")
        blockquote_content.set("class", f"fr-text--{self.options['size']}")

        blockquote_figcaption = etree.SubElement(blockquote_figure, "figcaption")
        blockquote_author = etree.SubElement(blockquote_figcaption, "p")
        blockquote_author.set("class", "fr-quote__author")
        blockquote_author.text = self.argument
        if self.options["image"]:
            blockquote_image = etree.SubElement(blockquote_figcaption, "div")
            blockquote_image.set("class", "fr-quote__image")
            img = etree.SubElement(blockquote_image, "img")
            img.set("class", "fr-responsive-img")
            img.set("src", self.options["image"])
            img.set("alt", "")

        return blockquote_content

    def _option(self, option):
        """Return the option value, ro empty string if not set."""
        if self.options[option]:
            return self.options[option]
        return ""

    def _option_bool(self, option, value):
        """Return the option value, or empty string if not set."""
        if self.options[option]:
            return value
        return ""


class DsfrQuoteExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrQuote, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrQuoteExtension(*args, **kwargs)
