from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_boolean, type_string_in,type_string
import xml.etree.ElementTree as etree


class DsfrNotice(Block):
    NAME = "notice"
    ARGUMENT = None
    OPTIONS = {
        "type": ("info", type_string_in(["info", "warning", "alert", "weather-orange", "weather-red", "weather-purple", "kidnapping", "cyberattack", "attack", "witness"])),
        "markup": ("p", type_string_in(["p","h1","h2","h3","h4","h5","h6"])),
        "icon" : ("", type_string),
        "link_label": ("", type_string),
        "link_url": ("", type_string),
        "link_title": ("", type_string),
        "link_newtab": (False, type_boolean),
    }

    count = 0

    def on_create(self, parent):
        # <div id="1" class="fr-notice fr-notice--info">
        # <div class="fr-container">
        #     <div class="fr-notice__body">
        #     <p>
        #         <span class="fr-notice__title fr-icon-xxx">Titre du bandeau</span>
        #         <span class="fr-notice__desc">Texte de description</span>
        #         <a href="#" target="_blank" rel="noopener external" class="fr-notice__link">Lien de consultation</a>
        #     </p>
        #     </div>
        # </div>
        # </div>

        notice_div = etree.SubElement(parent, "div")
        notice_div.set("class", f"fr-notice fr-notice--{self.options['type']}")
        notice_div.set("id", str(DsfrNotice.count))
        DsfrNotice.count += 1
        container_div = etree.SubElement(notice_div, "div")
        container_div.set("class", "fr-container")
        body_div = etree.SubElement(container_div, "div")
        body_div.set("class", "fr-notice__body")
        markup = self.options["markup"]
        content = etree.SubElement(body_div, markup)
        title_span = etree.SubElement(content, "span")
        icon_class = ""
        if self.options['icon']:
            icon_class = f"fr-icon-{self.options['icon']}"
        title_span.set("class", f"fr-notice__title {icon_class}")
        title_span.text = self.argument
        desc_span = etree.SubElement(content, "span")
        desc_span.set("class", "fr-notice__desc")
        if self.options["link_label"]:
            link = etree.SubElement(content, "a")
            link.set("class", "fr-notice__link")
            if self.options["link_url"]:
                link.set("href", self.options["link_url"])
            if self.options["link_newtab"]:
                link.set("target", "_blank")
                link.set("rel", "noopener external")
                if self.options["link_title"]:
                    link.set("title", self.options["link_title"])
            link.text = self.options["link_label"]
        return desc_span


class DsfrNoticeExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrNotice, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrNoticeExtension(*args, **kwargs)
