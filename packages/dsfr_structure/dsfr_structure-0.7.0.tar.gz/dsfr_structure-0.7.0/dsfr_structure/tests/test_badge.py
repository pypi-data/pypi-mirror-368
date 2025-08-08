# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.badge import DsfrBadgeExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestBadgeExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrBadgeExtension()])

    def test_case1(self):
        # given
        test_case = """
/// badge
Lorem ipsum dolor.
///
"""
        expected_output = """
        <p class="fr-badge">Lorem ipsum dolor.</p>
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
/// badge
    type: success
Lorem ipsum dolor.
///
"""
        expected_output = """
        <p class="fr-badge fr-badge--success">Lorem ipsum dolor.</p>
        """

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output

    def test_case3(self):
        # given
        test_case = """
/// badge
    type: warning
    icon: False
Lorem ipsum dolor.
///
"""
        expected_output = """
        <p class="fr-badge fr-badge--warning fr-badge--no-icon">Lorem ipsum dolor.</p>
        """

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output

    def test_case4(self):
        # given
        test_case = """
/// badge
    color: green-menthe
Lorem ipsum dolor.
///
"""
        expected_output = """
        <p class="fr-badge fr-badge--green-menthe">Lorem ipsum dolor.</p>
        """

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
