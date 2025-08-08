# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.callout import DsfrCalloutExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestCalloutExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrCalloutExtension()])

    def test_case1(self):
        # given
        test_case = """
/// callout | Mise en avant
    color: purple-glycine
    markup: h3
    icon: info-line
    link_label: En savoir plus
    link_url: http://www.example.com
    link_newtab: True
Voici le texte du callout, sachant que le bouton est forcément situé apres ce texte
///
"""
        expected_output = """
        <div id="0" class="fr-callout fr-icon-info-line fr-callout--purple-glycine">
          <h3 class="fr-callout__title">Mise en avant</h3>
          <p class="fr-callout__text">Voici le texte du callout, sachant que le bouton est forcément situé apres ce texte</p>
          <a class="fr-btn" href="http://www.example.com" rel="noopener external" target="_blank" title="En savoir plus - nouvelle fenêtre">En savoir plus</a>
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
/// callout
Callout minimal
///
"""
        expected_output = """
        <div id="1" class="fr-callout">
            <p class="fr-callout__text">Callout minimal</p>
        </div>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
