def absolute_url_if_needed(url):
    if contains_subpath(url):
        if url.endswith("/"):
            return url[:-1]
        return url
    return ""

def contains_subpath(url):
    """Check if the URL contains a subpath, ie it contains a slash in the path, except http(s):// or at the end."""
    if not url:
        return False
    # Check if the URL starts with http:// or https://
    if url.startswith("http://") or url.startswith("https://"):
        # Remove the protocol part
        url = url.split("://", 1)[1]
    # Remove the trailing slash if it exists
    if url.endswith("/"):
        url = url[:-1]
    # Check if there is a slash in the path
    return "/" in url
