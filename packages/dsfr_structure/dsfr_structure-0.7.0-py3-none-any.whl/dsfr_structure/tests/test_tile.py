# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.tile import DsfrTileExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestTileExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrTileExtension({"site_url": ""})])

    def test_case1(self):
        # given
        test_case = """
/// tile | Intitulé de la tuile
    picto: buildings/city-hall
    target: example.com
Détail (optionnel)
///
"""

        expected_output = """
<div class="fr-tile fr-enlarge-link" id="tile-0">
    <div class="fr-tile__body">
    <div class="fr-tile__content">
        <h5 class="fr-tile__title">
        <a href="example.com">Intitulé de la tuile</a>
        </h5>
        <p class="fr-tile__detail">Détail (optionnel)</p>
    </div>
    </div>
    <div class="fr-tile__header">
    <div class="fr-tile__pictogram">
        <svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="80px" height="80px">
        <use class="fr-artwork-decorative" href="/artwork/pictograms/buildings/city-hall.svg#artwork-decorative"></use>
        <use class="fr-artwork-minor" href="/artwork/pictograms/buildings/city-hall.svg#artwork-minor"></use>
        <use class="fr-artwork-major" href="/artwork/pictograms/buildings/city-hall.svg#artwork-major"></use>
        </svg>
    </div>
    </div>
</div>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output

    def test_case2(self):
        # given
        test_case = """
/// tile | Intitulé de la tuile
    picto: buildings/city-hall
    target: example.com
    target_new: True
    lang: en
    assess: True
    download: True
    markup: h4
Détail (optionnel)
///
"""

        expected_output = """
<div class="fr-tile fr-tile--download fr-enlarge-link" id="tile-1">
    <div class="fr-tile__body">
    <div class="fr-tile__content">
        <h4 class="fr-tile__title">
        <a hreflang="en" data-fr-assess-file download href="example.com" target="_blank" title="Intitulé de la tuile - nouvelle fenêtre" rel="noopener external">Intitulé de la tuile</a>
        </h4>
        <p class="fr-tile__detail">Détail (optionnel)</p>
    </div>
    </div>
    <div class="fr-tile__header">
    <div class="fr-tile__pictogram">
        <svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="80px" height="80px">
        <use class="fr-artwork-decorative" href="/artwork/pictograms/buildings/city-hall.svg#artwork-decorative"></use>
        <use class="fr-artwork-minor" href="/artwork/pictograms/buildings/city-hall.svg#artwork-minor"></use>
        <use class="fr-artwork-major" href="/artwork/pictograms/buildings/city-hall.svg#artwork-major"></use>
        </svg>
    </div>
    </div>
</div>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
