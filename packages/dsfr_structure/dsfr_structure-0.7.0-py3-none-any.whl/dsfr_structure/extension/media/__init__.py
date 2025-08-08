from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_string, type_string_in
import xml.etree.ElementTree as etree


class DsfrMedia(Block):
    NAME = "media"
    ARGUMENT = None
    OPTIONS = {
        "type": ("video", type_string_in(["video"])),
        "url": ("", type_string),
        "captions": ("", type_string),
        "poster": ("", type_string)
    }

    count = 0

    def on_create(self, parent):
        # <figure id="video-n" role="group" class="fr-content-media">
        #     <video src='https://aide.din.developpement-durable.gouv.fr/fichiers/Dnum.mp4' poster="../videos/video.png" class="fr-responsive-vid" controls>
        #         <track kind="captions" label="Francais" src="../videos/video.vtt" srclang="fr" default />
        #     </video>
        #     <figcaption class="fr-content-media__caption">
        #         Vidéo d'explication des visio-conférences / Dnum 2024
        #     </figcaption>
        # </figure>

        media_id = "video-%s" % DsfrMedia.count
        DsfrMedia.count += 1

        media_figure = etree.SubElement(parent, "figure")
        media_figure.set("id", media_id)
        media_figure.set("role", "group")
        media_figure.set("class", "fr-content-media")
        media_video = etree.SubElement(media_figure, "video")
        media_video.set("class", "fr-responsive-vid")
        media_video.set("controls", "")
        if self.options["poster"]:
            media_video.set("poster", self.options["poster"])
        if self.options["url"]:
            media_video.set("src", self.options["url"])
        if self.options["captions"]:
            track = etree.SubElement(media_video, "track")
            track.set("kind", "captions")
            track.set("label", "Français")
            track.set("src", self.options["captions"])
            track.set("srclang", "fr")
            track.set("default", "")
        if self.argument:
            figcaption = etree.SubElement(media_figure, "figcaption")
            figcaption.set("class", "fr-content-media__caption")
            figcaption.text = self.argument

        return media_figure

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

class DsfrMediaExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):

        block_mgr.register(DsfrMedia, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DsfrMediaExtension(*args, **kwargs)
