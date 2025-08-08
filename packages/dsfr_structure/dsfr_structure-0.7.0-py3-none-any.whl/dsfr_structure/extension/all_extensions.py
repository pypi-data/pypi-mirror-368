import logging

import yaml
from markdown.extensions import Extension

from dsfr_structure.extension import (
    accordion,
    alert,
    badge,
    blockquote,
    callout,
    card,
    col,
    media,
    notice,
    quote,
    row,
    table,
    tile,
)

logger = logging.getLogger(__name__)

class AllExtensions(Extension):

    def __init__(self, mkdocs_config: dict | None = None,  **kwargs):
        """Initialize the extension."""
        super().__init__(**kwargs)
        if mkdocs_config is None:
            mkdocs_config = extract_mkdocs_conf()
        self.mkdocs_config = mkdocs_config

    def extendMarkdown(self, md):
        blockquote_ext = blockquote.DsfrBlockQuoteExtension()
        blockquote_ext.extendMarkdown(md)

        table_ext = table.DsfrTableExtension()
        table_ext.extendMarkdown(md)

        accordion_ext = accordion.DsfrAccordionExtension()
        accordion_ext.extendMarkdown(md)

        alert_ext = alert.DsfrAlertExtension()
        alert_ext.extendMarkdown(md)

        badge_ext = badge.DsfrBadgeExtension()
        badge_ext.extendMarkdown(md)

        row_ext = row.DsfrRowExtension()
        row_ext.extendMarkdown(md)

        col_ext = col.DsfrColExtension()
        col_ext.extendMarkdown(md)

        tile_ext = tile.DsfrTileExtension(self.mkdocs_config)
        tile_ext.extendMarkdown(md)

        card_ext = card.DsfrCardExtension()
        card_ext.extendMarkdown(md)

        notice_ext = notice.DsfrNoticeExtension()
        notice_ext.extendMarkdown(md)

        callout_ext = callout.DsfrCalloutExtension()
        callout_ext.extendMarkdown(md)

        quote_ext = quote.DsfrQuoteExtension()
        quote_ext.extendMarkdown(md)

        media_ext = media.DsfrMediaExtension()
        media_ext.extendMarkdown(md)

class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None  # ou tu peux retourner node.value si tu veux garder la valeur brute

SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)

def makeExtension(**kwargs):
    return AllExtensions(**kwargs)

def extract_mkdocs_conf():
    possible_paths = ['mkdocs.yml', 'mkdocs.yaml']
    for current_path in possible_paths:
        try:
            with open(current_path, 'r', encoding='utf-8') as f:
                conf =  yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
                if conf is not None:
                    return conf
        except FileNotFoundError:
            continue
        except Exception as e:
            logger.warning(f"Erreur lors de la lecture du fichier {current_path}: {e}")
    logger.warning("Aucun fichier de configuration mkdocs trouvé.")
    return {}
