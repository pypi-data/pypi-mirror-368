# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.quote import DsfrQuoteExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestQuoteExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrQuoteExtension()])

    def test_case1(self):
        # given
        test_case = """
/// quote | Victor Hugo
    image: https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Victor_Hugo_001.jpg/330px-Victor_Hugo_001.jpg
    size: lg
    color: green-menthe
« Notre devise est : Liberté, Egalité, Fraternité ! Victor Hugo décrivait notre devise comme étant les trois marches du perron suprême et que le mot le plus fort était celui de Fraternité »
///
"""
        expected_output = """
        <figure id="blockquote-0" class="fr-quote fr-quote--column fr-quote--green-menthe ">
          <blockquote>
            <p class="fr-text--lg">« Notre devise est : Liberté, Egalité, Fraternité ! Victor Hugo décrivait notre devise comme étant les trois marches du perron suprême et que le mot le plus fort était celui de Fraternité »</p>
          </blockquote>
          <figcaption>
            <p class="fr-quote__author">Victor Hugo</p>
            <div class="fr-quote__image">
              <img class="fr-responsive-img" src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Victor_Hugo_001.jpg/330px-Victor_Hugo_001.jpg" alt="" />
            </div>
          </figcaption>
        </figure>
"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
