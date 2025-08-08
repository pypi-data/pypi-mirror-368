from xml.etree.ElementTree import Element

from markdown.extensions import Extension
from markdown.extensions.tables import TableProcessor


class DsfrTableProcessor(TableProcessor):

    def __init__(self, parser, config):
        super().__init__(parser, config)

    def run(self, parent, blocks):
        super().run(parent, blocks)

        if len(parent) > 0 and parent[-1].tag == 'table':
            table = parent[-1]
            div = Element('div')
            div.set('class', 'fr-table')
            div.append(table)
            parent[-1] = div


class DsfrTableExtension(Extension):

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(DsfrTableProcessor(md.parser, self.getConfigs()), 'table', 75)


def makeExtension(**kwargs):
    return DsfrTableExtension(**kwargs)
