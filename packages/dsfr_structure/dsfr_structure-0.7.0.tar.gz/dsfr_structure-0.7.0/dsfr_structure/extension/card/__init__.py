from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_boolean, type_string, type_string_in
import xml.etree.ElementTree as etree


class DsfrCard(Block):
    NAME = "card"
    ARGUMENT = None
    OPTIONS = {
        "description": ("", type_string),
        "badge": ("", type_string), # "Texte du badge | id couleur"
        "tag": ("", type_string), # "Texte du tag | id couleur"
        "picto": ("", type_string), # Chemin picto sans extension : buildings/city-hall
        "markup": ("h5", type_string_in(["p", "h1", "h2", "h3", "h4", "h5", "h6"])),
        "enlarge": (True, type_boolean),
        "target": ("", type_string),
        "target_new": (False, type_boolean),
        "image": ("", type_string),
        "image_alt": ("", type_string),
        "download": (False, type_boolean),
        "lang": ("", type_string),
        "assess": (False, type_boolean),
#        "small": (False, type_boolean),
        "horizontal": (False, type_boolean),
        "horizontal_pos": ("", type_string_in(["", "tier", "half"])),
#        "vertical_breakpoint": ("", type_string_in(["", "md", "lg"])),
        "variations": ("", type_string_in(["", "grey", "no-border", "no-background", "shadow"])),
    }

    count = 0

    def on_create(self, parent):
        # <div id="106" class="fr-card fr-enlarge-link fr-card--horizontal-tier fr-card--download fr-card--grey">
        #   <div class="fr-card__body">
        #     <div class="fr-card__content">
        #       <h5 class="fr-card__title">
        #         <a title="titre" hreflang="fr" data-fr-assess-file download href="[URL - à modifier]" target="_blank" rel="noopener external">Intitulé de la carte</a>
        #       </h5>
        #       <p class="fr-card__desc">Lorem ipsum dolor sit amet, consectetur adipiscing, incididunt, ut labore et dolore magna aliqua. Vitae sapien pellentesque habitant morbi tristique senectus et</p>
        #       <div class="fr-card__start">
        #         <ul class="fr-badges-group">
        #           <li>
        #             <p class="fr-badge fr-badge--purple-glycine">Libellé badge</p>
        #           </li>
        #           <li>
        #             <p class="fr-badge fr-badge--purple-glycine">Libellé badge</p>
        #           </li>
        #         </ul>
        #         <p class="fr-card__detail fr-icon-warning-fill">détail (optionnel)</p>
        #       </div>
        #       <div class="fr-card__end">
        #         <p class="fr-card__detail fr-icon-warning-fill">détail (optionnel)</p>
        #       </div>
        #     </div>
        #   </div>
        #   <div class="fr-card__header">
        #     <div class="fr-card__img">
        #       <img class="fr-responsive-img" src="img/placeholder.16x9.png" alt="[À MODIFIER - vide ou texte alternatif de l’image]" />
        #       <!-- L’alternative de l’image (attribut alt) doit toujours être présente, sa valeur peut-être vide (image n’apportant pas de sens supplémentaire au contexte) ou non (porteuse de texte ou apportant du sens) selon votre contexte -->
        #     </div>
        #     <ul class="fr-badges-group">
        #       <li>
        #         <p class="fr-badge fr-badge--purple-glycine">Libellé badge</p>
        #       </li>
        #     </ul>
        #   </div>
        # </div>
        card_id = "card-%s" % DsfrCard.count
        DsfrCard.count += 1

        # <div id="106" class="fr-card fr-enlarge-link fr-card--horizontal-tier fr-card--download fr-card--grey">
        card_div = etree.SubElement(parent, "div")

        variations = self._option("variations")
        if variations:
            variations = f"fr-card--{variations}"
        else:
            variations = ""
        horizontal = ""
        if self.options["horizontal"]:
            if self.options["horizontal_pos"]:
                horizontal = f"fr-card--horizontal-{self.options['horizontal_pos']}"
            else:
                horizontal = "fr-card--horizontal"
        card_div.set("class", f"fr-card {horizontal} {variations} {self._option_bool('download', 'fr-card--download')} {self._option_bool('enlarge', 'fr-enlarge-link')}")
        card_div.set("id", card_id)

        # <div class="fr-card__body">
        body_div = etree.SubElement(card_div, "div")
        body_div.set("class", "fr-card__body")

        # <div class="fr-card__content">
        content_div = etree.SubElement(body_div, "div")
        content_div.set("class", "fr-card__content")

        # <h5 class="fr-card__title">
        h5 = etree.SubElement(content_div, self.options["markup"])
        h5.set("class", "fr-card__title")

        # <a title="toto - nouvelle fenêtre" data-fr-assess-file download href="img/placeholder.16x9.png" target="_blank" rel="noopener external">Intitulé de la tuile</a>
        a = etree.SubElement(h5, "a")
        if self.options["assess"]:
            a.set("data-fr-assess-file", "")
        if self.options["lang"]:
            a.set("hreflang", self.options["lang"])
        if self.options["download"]:
            a.set("download", "")
        if self.options["target"]:
            a.set("href", self.options["target"])
        if self.options["target_new"]:
            a.set("target", "_blank")
            a.set("rel", "noopener external")
            a.set("title", f'{self.argument} - nouvelle fenêtre')
        a.text = self.argument

        # <p class="fr-card__desc">Description (optionnelle)</p>
        if self.options["description"]:
            desc = etree.SubElement(content_div, "p")
            desc.set("class", "fr-card__desc")
            desc.text = self.options["description"]

        # <div class="fr-card__start">
        # Label ou tag ...
        # <p class="fr-tag">Libellé tag</p>
        if self.options["badge"]:
            tag_args = self.options["badge"].split("|")
            start_div = etree.SubElement(content_div, "div")
            start_div.set("class", "fr-card__start")
            tag = etree.SubElement(start_div, "p")
            tag.text = tag_args[0].strip()
            if len(tag_args) > 1:
                tag.set("class", f"fr-badge fr-badge--{tag_args[1].strip()}")
            else:
                tag.set("class", "fr-badge")
        elif self.options["tag"]:
            tag_args = self.options["tag"].split("|")
            start_div = etree.SubElement(content_div, "div")
            start_div.set("class", "fr-card__start")
            tag = etree.SubElement(start_div, "p")
            tag.text = tag_args[0].strip()
            if len(tag_args) > 1:
                tag.set("class", f"fr-tag fr-tag--{tag_args[1].strip()}")
            else:
                tag.set("class", "fr-tag")

        #       <div class="fr-card__end">
        #         <p class="fr-card__detail fr-icon-warning-fill">...</p>
        end = etree.SubElement(content_div, "div")
        end.set("class", "fr-card__end")
        detail = etree.SubElement(end, "p")
        detail.set("class", "fr-card__detail")

        # <div class="fr-card__header">
        if self.options["image"]:
            header_div = etree.SubElement(card_div, "div")
            header_div.set("class", "fr-card__header")

            #     <div class="fr-card__img">
            img_div = etree.SubElement(header_div, "div")
            img_div.set("class", "fr-card__img")

            #       <img class="fr-responsive-img" src="img/placeholder.16x9.png" alt="[À MODIFIER - vide ou texte alternatif de l’image]" />
            #       <!-- L’alternative de l’image (attribut alt) doit toujours être présente, sa valeur peut-être vide (image n’apportant pas de sens supplémentaire au contexte) ou non (porteuse de texte ou apportant du sens) selon votre contexte -->
            img = etree.SubElement(img_div, "img")
            img.set("class", "fr-responsive-img")
            img.set("src", self.options["image"])
            img.set("alt", self._option("image_alt"))

        return detail

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


class DsfrCardExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrCard, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrCardExtension(*args, **kwargs)
