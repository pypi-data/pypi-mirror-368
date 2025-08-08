# test.py
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.accordion import DsfrAccordionExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


class TestAccordionExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrAccordionExtension()])

    def test_case1(self):
        # given
        test_case = """
/// accordion | Titre
Lorem ipsum dolor.
///
/// accordion | Titre2
Lorem ipsum dolor2.
///
"""

        expected_output = """
<section class="fr-accordion">
    <h5 class="fr-accordion__title">
        <button class="fr-accordion__btn" aria-expanded="false" aria-controls="accordion-0">Titre</button>
    </h5>
    <div class="fr-collapse" id="accordion-0">
        <p>
        Lorem ipsum dolor.
        </p>
    </div>
</section>
<section class="fr-accordion">
    <h5 class="fr-accordion__title">
        <button class="fr-accordion__btn" aria-expanded="false" aria-controls="accordion-1">Titre2</button>
    </h5>
    <div class="fr-collapse" id="accordion-1">
        <p>
        Lorem ipsum dolor2.
        </p>
    </div>
</section>"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)
        expected_output = remove_whitespaces_and_indentations(expected_output)

        # then
        assert expected_output == html_output
