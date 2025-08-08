# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.col import DsfrColExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestRowExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrColExtension()])

    def test_case1(self):
        # given
        test_case = """
/// col
Lorem ipsum dolor.
///
"""

        expected_output = """
<div class="fr-col"><p>Lorem ipsum dolor.</p></div>
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
/// col | 12 md-6
Lorem ipsum dolor.
///
"""

        expected_output = """
<div class="fr-col-12 fr-col-md-6"><p>Lorem ipsum dolor.</p></div>
"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
