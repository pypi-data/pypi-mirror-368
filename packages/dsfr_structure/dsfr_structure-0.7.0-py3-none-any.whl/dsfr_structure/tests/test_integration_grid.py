# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.all_extensions import AllExtensions


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestRowExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[AllExtensions({"site_url": ""})])

    def test_case1(self):
        # given
        test_case = """
/// row
/// col
Col 1
///
/// col | 4
Col 2
///
/// col | 12 lg-4
Col 3
///
///
"""

        expected_output = """
<div class="fr-grid-row">
    <div class="fr-col">
        <p>Col 1</p>
    </div>
    <div class="fr-col-4">
        <p>Col 2</p>
    </div>
    <div class="fr-col-12 fr-col-lg-4">
        <p>Col 3</p>
    </div>
"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output

    def test_case2(self):
        # given
        test_case = """
/// row | fr-grid-row--gutters
    halign: center
    valign: bottom
Lorem ipsum dolor.
///
"""

        expected_output = """
<div class="fr-grid-row fr-grid-row--gutters fr-grid-row--center fr-grid-row--bottom"><p>Lorem ipsum dolor.</p></div>
"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
