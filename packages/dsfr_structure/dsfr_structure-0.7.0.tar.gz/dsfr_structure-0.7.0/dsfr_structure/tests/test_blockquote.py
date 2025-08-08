# test.py
import unittest
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.blockquote import DsfrBlockQuoteExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.prettify()


class TestBlockquotesExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrBlockQuoteExtension()])

    def test_case1(self):
        # given
        test_case = """> line 1
        > line 2
        > line 3"""

        expected_output = """<div class="fr-highlight">
             <p>
                  line 1 <br/>
                  line 2 <br/>
                  line 3
             </p>
        </div>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output


if __name__ == '__main__':
    unittest.main()
