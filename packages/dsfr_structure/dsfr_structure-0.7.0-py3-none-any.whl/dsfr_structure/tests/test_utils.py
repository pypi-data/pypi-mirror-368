from dsfr_structure.extension.utils import contains_subpath
from dsfr_structure.extension.utils import absolute_url_if_needed

def test_contains_subpath_valid():
    assert contains_subpath("http://example.com/path/to/resource") is True
    assert contains_subpath("https://example.com/path/to/resource") is True
    assert contains_subpath("http://example.com/path/") is True
    assert contains_subpath("https://example.com/path/") is True
    assert contains_subpath("http://example.com/") is False
    assert contains_subpath("https://example.com/") is False
    assert contains_subpath("http://example.com") is False
    assert contains_subpath("https://example.com") is False
    assert contains_subpath("") is False
    assert contains_subpath(None) is False

def test_absolute_url_if_needed():
    assert absolute_url_if_needed("http://example.com/path/to/resource") == "http://example.com/path/to/resource"
    assert absolute_url_if_needed("https://example.com/path/to/resource/") == "https://example.com/path/to/resource"
    assert absolute_url_if_needed("http://example.com/path/") == "http://example.com/path"
    assert absolute_url_if_needed("https://example.com/path") == "https://example.com/path"
    assert absolute_url_if_needed("http://example.com/") == ""
    assert absolute_url_if_needed("https://example.com/") == ""
    assert absolute_url_if_needed("http://example.com") == ""
    assert absolute_url_if_needed("https://example.com") == ""
    assert absolute_url_if_needed("") == ""
    assert absolute_url_if_needed(None) == ""
