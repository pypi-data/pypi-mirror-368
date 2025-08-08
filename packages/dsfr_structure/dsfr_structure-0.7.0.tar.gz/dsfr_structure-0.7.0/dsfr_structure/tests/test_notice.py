# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.notice import DsfrNoticeExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestNoticeExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrNoticeExtension()])

    def test_case1(self):
        # given
        test_case = """
/// notice | Titre
Lorem ipsum dolor.
///
"""
        expected_output = """
        <div id="0" class="fr-notice fr-notice--info">
        <div class="fr-container">
            <div class="fr-notice__body">
            <p>
                <span class="fr-notice__title">Titre</span>
                <span class="fr-notice__desc">Lorem ipsum dolor.</span>
            </p>
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
/// notice | Titre du bandeau
    type: warning
    markup: h5
    icon: checkbox-circle-line
    link_label: Lien de consultation
    link_url: "#"
    link_title: Lien
    link_newtab: True
Texte de description
///
"""
        expected_output = """
        <div id="1" class="fr-notice fr-notice--warning">
        <div class="fr-container">
            <div class="fr-notice__body">
            <h5>
                <span class="fr-notice__title fr-icon-checkbox-circle-line">Titre du bandeau</span>
                <span class="fr-notice__desc">Texte de description</span>
                <a href="#" target="_blank" rel="noopener external" class="fr-notice__link" title="Lien">Lien de consultation</a>
            </h5>
            </div>
        </div>
        </div>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
