# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.card import DsfrCardExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestCardExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrCardExtension()])

    def test_case1(self):
        # given
        test_case = """
/// card | Intitulé de la carte
    image: /img/placeholder.16x9.png
    target: example.com
    markup: h4
Détail (optionnel)
///
"""

        expected_output = """
        <div id="card-0" class="fr-card fr-enlarge-link">
          <div class="fr-card__body">
            <div class="fr-card__content">
              <h4 class="fr-card__title">
                <a href="example.com">Intitulé de la carte</a>
              </h4>
              <div class="fr-card__end">
                <p class="fr-card__detail">Détail (optionnel)</p>
              </div>
            </div>
          </div>
          <div class="fr-card__header">
            <div class="fr-card__img">
              <img class="fr-responsive-img" src="/img/placeholder.16x9.png" alt="" />
            </div>
          </div>
        </div>
"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output

    def test_case_noimage(self):
        # given
        test_case = """
/// card | Intitulé de la carte
    target: example.com
    markup: h4
Détail (optionnel)
///
"""

        expected_output = """
        <div id="card-1" class="fr-card fr-enlarge-link">
          <div class="fr-card__body">
            <div class="fr-card__content">
              <h4 class="fr-card__title">
                <a href="example.com">Intitulé de la carte</a>
              </h4>
              <div class="fr-card__end">
                <p class="fr-card__detail">Détail (optionnel)</p>
              </div>
            </div>
          </div>
        </div>
"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
