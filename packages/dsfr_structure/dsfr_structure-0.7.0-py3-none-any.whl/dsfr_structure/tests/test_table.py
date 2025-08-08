import unittest
from xml.etree.ElementTree import fromstring, tostring

import markdown
from bs4 import BeautifulSoup

from dsfr_structure.extension.table import DsfrTableExtension


def normalize_html(html: str) -> str:
    return tostring(fromstring(html)).decode()


def remove_whitespaces_and_indentations(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.prettify()


class TestTableExtension:

    def setup_method(self):
        self.md = markdown.Markdown(extensions=[DsfrTableExtension()])

    def test_case1(self):
        # given
        test_case = """ | Day       | Breakfast               | Lunch                 | Dinner                    |
                        |-----------|-------------------------|-----------------------|---------------------------|
                        | Monday    | Avocado Toast & Coffee  | Grilled Chicken Salad | Spaghetti Carbonara       |
                        | Tuesday   | Greek Yogurt & Berries  | Tuna Sandwich         | Grilled Salmon            |
                        | Wednesday | Oatmeal & Green Tea     | Chicken Caesar Wrap   | Stir-Fry Vegetables       |
                        | Thursday  | Scrambled Eggs & Toast  | Vegetable Soup        | Beef Stroganoff           |
                        | Friday    | Pancakes & Orange Juice | BLT Sandwich          | Margherita Pizza          |
                        | Saturday  | French Toast & Smoothie | Chicken Quesadilla    | BBQ Ribs                  |
                        | Sunday    | Bagel & Cream Cheese    | Steak Salad           | Roasted Chicken & Veggies |"""

        # when
        html_output = self.md.convert(test_case)

        html_output = remove_whitespaces_and_indentations(html_output)

        # then
        assert html_output.startswith('<div class="fr-table">')


if __name__ == '__main__':
    unittest.main()
