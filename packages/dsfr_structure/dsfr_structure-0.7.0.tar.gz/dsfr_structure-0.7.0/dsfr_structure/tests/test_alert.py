# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.alert import DsfrAlertExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestAlertExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrAlertExtension()])

    def test_case1(self):
        # given
        test_case = """
/// alert | Titre
Lorem ipsum dolor.
///
"""
        expected_output = """
        <div class="fr-alert fr-alert--info">
            <h5 class="fr-alert__title">Titre</h5>
            <p>Lorem ipsum dolor.</p>
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
/// alert | Titre
    type: success
Lorem ipsum dolor.
///
"""

        expected_output = """
        <div class="fr-alert fr-alert--success">
            <h5 class="fr-alert__title">Titre</h5>
            <p>Lorem ipsum dolor.</p>
        </div>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output

    def test_case3(self):
        # given
        test_case = """
/// alert | Titre h4
    markup: h4
    type: info
Lorem ipsum dolor.
///
"""

        expected_output = """
        <div class="fr-alert fr-alert--info">
            <h4 class="fr-alert__title">Titre h4</h4>
            <p>Lorem ipsum dolor.</p>
        </div>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
