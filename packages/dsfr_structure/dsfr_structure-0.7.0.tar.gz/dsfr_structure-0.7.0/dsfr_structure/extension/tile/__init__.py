from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_boolean, type_string, type_string_in
import xml.etree.ElementTree as etree

from mkdocs.config.base import load_config
from dsfr_structure.extension.utils import absolute_url_if_needed

class DsfrTile(Block):
    NAME = "tile"
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
        "download": (False, type_boolean),
        "lang": ("", type_string),
        "assess": (False, type_boolean),
        "small": (False, type_boolean),
        "horizontal": (False, type_boolean),
        "vertical_breakpoint": ("", type_string_in(["", "md", "lg"])),
        "variations": ("", type_string_in(["", "grey", "no-border", "no-background", "shadow"])),
    }

    count = 0

    def on_create(self, parent):
        # <div class="fr-tile fr-tile--sm fr-tile--horizontal fr-tile--vertical@md fr-tile--shadow fr-tile--download fr-enlarge-link" id="tile-122">
        #   <div class="fr-tile__body">
        #     <div class="fr-tile__content">
        #       <h5 class="fr-tile__title">
        #         <a title="toto - nouvelle fenêtre" data-fr-assess-file download hreflang="fr" href="img/placeholder.16x9.png" target="_blank" rel="noopener external">Intitulé de la tuile</a>
        #       </h5>
        #       <p class="fr-tile__desc">Description (optionnelle)</p>
        #       <p class="fr-tile__detail">...</p>
        #       <div class="fr-tile__start">
        #         <p class="fr-tag">Libellé tag</p>
        #       </div>
        #     </div>
        #   </div>
        #   <div class="fr-tile__header">
        #     <div class="fr-tile__pictogram">
        #       <svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="80px" height="80px">
        #         <use class="fr-artwork-decorative" href="/dist/artwork/pictograms/buildings/city-hall.svg#artwork-decorative"></use>
        #         <use class="fr-artwork-minor" href="/dist/artwork/pictograms/buildings/city-hall.svg#artwork-minor"></use>
        #         <use class="fr-artwork-major" href="/dist/artwork/pictograms/buildings/city-hall.svg#artwork-major"></use>
        #       </svg>
        #     </div>
        #   </div>
        # </div>
        tile_id = "tile-%s" % DsfrTile.count
        DsfrTile.count += 1

        # <div class="fr-tile fr-tile--sm fr-tile--horizontal fr-tile--vertical@md fr-tile--shadow fr-tile--download fr-enlarge-link" id="tile-122">
        tile_div = etree.SubElement(parent, "div")

        vertical_breakpoint = self._option("vertical_breakpoint")
        if vertical_breakpoint:
            vertical_breakpoint = f"fr-tile--vertical@{vertical_breakpoint}"
        else:
            vertical_breakpoint = ""
        variations = self._option("variations")
        if variations:
            variations = f"fr-tile--{variations}"
        else:
            variations = ""
        tile_div.set("class", f"fr-tile {self._option_bool('small','fr-tile--sm')} {self._option_bool('horizontal', 'fr-tile--horizontal')} {vertical_breakpoint} {variations} {self._option_bool('download', 'fr-tile--download')} {self._option_bool('enlarge', 'fr-enlarge-link')}")
        tile_div.set("id", tile_id)

        # <div class="fr-tile__body">
        body_div = etree.SubElement(tile_div, "div")
        body_div.set("class", "fr-tile__body")

        # <div class="fr-tile__content">
        content_div = etree.SubElement(body_div, "div")
        content_div.set("class", "fr-tile__content")

        # <h5 class="fr-tile__title">
        h5 = etree.SubElement(content_div, self.options["markup"])
        h5.set("class", "fr-tile__title")

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

        # <p class="fr-tile__desc">Description (optionnelle)</p>
        if self.options["description"]:
            desc = etree.SubElement(content_div, "p")
            desc.set("class", "fr-tile__desc")
            desc.text = self.options["description"]

        # <p class="fr-tile__detail">...</p>
        detail = etree.SubElement(content_div, "p")
        detail.set("class", "fr-tile__detail")

        # <div class="fr-tile__start">
        # Label ou tag ...
        # <p class="fr-tag">Libellé tag</p>
        if self.options["badge"]:
            tag_args = self.options["badge"].split("|")
            start_div = etree.SubElement(content_div, "div")
            start_div.set("class", "fr-tile__start")
            tag = etree.SubElement(start_div, "p")
            tag.text = tag_args[0].strip()
            if len(tag_args) > 1:
                tag.set("class", f"fr-badge fr-badge--{tag_args[1].strip()}")
            else:
                tag.set("class", "fr-badge")
        elif self.options["tag"]:
            tag_args = self.options["tag"].split("|")
            start_div = etree.SubElement(content_div, "div")
            start_div.set("class", "fr-tile__start")
            tag = etree.SubElement(start_div, "p")
            tag.text = tag_args[0].strip()
            if len(tag_args) > 1:
                tag.set("class", f"fr-tag fr-tag--{tag_args[1].strip()}")
            else:
                tag.set("class", "fr-tag")
        # <div class="fr-tile__header">
        header_div = etree.SubElement(tile_div, "div")
        header_div.set("class", "fr-tile__header")
        if self.options["picto"]:
            # <div class="fr-tile__pictogram">
            pictogram_div = etree.SubElement(header_div, "div")
            pictogram_div.set("class", "fr-tile__pictogram")
            # <svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="80px" height="80px">
            svg = etree.SubElement(pictogram_div, "svg")
            svg.set("aria-hidden", "true")
            svg.set("class", "fr-artwork")
            svg.set("viewBox", "0 0 80 80")
            svg.set("width", "80px")
            svg.set("height", "80px")

            # <use class="fr-artwork-decorative" href="/artwork/pictograms/buildings/city-hall.svg#artwork-decorative"></use>
            site_url = self.config.get("site_url", "")
            absolute_url_prefix = absolute_url_if_needed(site_url)
            use = etree.SubElement(svg, "use")
            use.set("class", "fr-artwork-decorative")
            use.set("href", f"{absolute_url_prefix}/artwork/pictograms/{self.options['picto']}.svg#artwork-decorative")
            # <use class="fr-artwork-minor" href="/artwork/pictograms/buildings/city-hall.svg#artwork-minor"></use>
            use = etree.SubElement(svg, "use")
            use.set("class", "fr-artwork-minor")
            use.set("href", f"{absolute_url_prefix}/artwork/pictograms/{self.options['picto']}.svg#artwork-minor")
            # <use class="fr-artwork-major" href="/artwork/pictograms/buildings/city-hall.svg#artwork-major"></use>
            use = etree.SubElement(svg, "use")
            use.set("class", "fr-artwork-major")
            use.set("href", f"{absolute_url_prefix}/artwork/pictograms/{self.options['picto']}.svg#artwork-major")

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

class DsfrTileExtension(BlocksExtension):

    def __init__(self, mkdocs_config: dict | None = None, **kwargs):
        """Initialize the extension."""
        super().__init__(**kwargs)
        self.mkdocs_config = mkdocs_config or load_config()

    def extendMarkdownBlocks(self, md, block_mgr):
        block_config = self.getConfigs()
        if "site_url" in self.mkdocs_config :
            block_config["site_url"] = self.mkdocs_config ["site_url"]

        block_mgr.register(DsfrTile, block_config)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrTileExtension(*args, **kwargs)
