# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.media import DsfrMediaExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestMediaExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrMediaExtension()])

    def test_case1(self):
        # given
        test_case = """
/// media | Vidéo d'explication des visio-conférences / Dnum 2024
    url: https://aide.din.developpement-durable.gouv.fr/fichiers/Dnum.mp4
    poster: ../videos/video.png
    captions: ../videos/video.vtt
///
"""
        expected_output = """
        <figure id="video-0" role="group" class="fr-content-media">
            <video src='https://aide.din.developpement-durable.gouv.fr/fichiers/Dnum.mp4' poster="../videos/video.png" class="fr-responsive-vid" controls>
                <track kind="captions" label="Français" src="../videos/video.vtt" srclang="fr" default />
            </video>
            <figcaption class="fr-content-media__caption">
                Vidéo d'explication des visio-conférences / Dnum 2024
            </figcaption>
        </figure>
"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
