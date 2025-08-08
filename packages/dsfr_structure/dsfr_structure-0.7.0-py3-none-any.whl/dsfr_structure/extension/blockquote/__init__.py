# dsfr_blockquote.py
import re
from xml.etree.ElementTree import Element

from markdown.blockprocessors import BlockQuoteProcessor
from markdown.extensions import Extension


class DsfrBlockQuoteProcessor(BlockQuoteProcessor):

    def run(self, parent, blocks):
        raw_block = blocks.pop(0)
        blockquote_content = self.process_blockquote(raw_block)
        self.append_custom_blockquote(parent, blockquote_content)

    def process_blockquote(self, raw_block):
        lines = self.split_lines(raw_block)
        cleaned_lines = [self.clean_line(line) for line in lines]
        return self.join_lines(cleaned_lines)

    @staticmethod
    def split_lines(block):
        return re.split(r'\n', block)

    @staticmethod
    def clean_line(line):
        return re.sub(r'^\s*>[ ]?', '', line)

    @staticmethod
    def join_lines(lines):
        return '<br />'.join(lines)

    def append_custom_blockquote(self, parent, content):
        div = self.create_custom_blockquote_element(content)
        parent.append(div)

    def create_custom_blockquote_element(self, content):
        div = Element('div')
        div.set('class', 'fr-highlight')
        self.parser.parseChunk(div, content)
        return div


class DsfrBlockQuoteExtension(Extension):

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(DsfrBlockQuoteProcessor(md.parser), 'quote', 60)


def makeExtension(**kwargs):
    return DsfrBlockQuoteExtension(**kwargs)
