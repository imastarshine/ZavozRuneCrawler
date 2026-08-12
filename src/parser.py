import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "link", "meta", "noscript"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    head = soup.head
    if head is not None:
        for tag in head(["script", "style", "link", "meta"]):
            tag.decompose()
    return soup.prettify()


def extract_links(html: str, base_url: str = "") -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        if base_url:
            href = urljoin(base_url, href)
        if href not in seen:
            seen.add(href)
            links.append(href)
    return links


def is_link(url: str) -> bool:
    return bool(urlparse(url).scheme)


def normalize_url(url: str) -> str:
    p = urlparse(url)
    scheme = (p.scheme or "http").lower()
    netloc = p.netloc.lower()
    path = "/" if p.path in ("", "/") else p.path
    query = f"?{p.query}" if p.query else ""
    return f"{scheme}://{netloc}{path}{query}"


_FILE_EXTENSIONS = {
    ".mp3", ".mp4", ".ogg", ".wav", ".flac", ".m4a", ".aac",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".bmp",
    ".webm", ".mov", ".avi", ".mkv", ".pdf", ".zip", ".gz", ".7z",
}


def is_allowed_domain(url: str, base_url: str) -> bool:
    url_host = urlparse(url).netloc.lower()
    base_host = urlparse(base_url).netloc.lower()
    if url_host.startswith("www."):
        url_host = url_host[4:]
    if base_host.startswith("www."):
        base_host = base_host[4:]
    return url_host == base_host and bool(url_host)


_MAGIC_FILE_PREFIXES = (
    b"\x89PNG\r\n\x1a\n",
    b"\xff\xd8\xff",
    b"GIF87a",
    b"GIF89a",
    b"ID3",
    b"\x00\x00\x00\x18ftyp",
    b"fLaC",
    b"OggS",
    b"%PDF",
    b"PK\x03\x04",
    b"\x1aE\xdf\xa3",
)


def detect_type(content_type: str, url: str, content: bytes | str = b"") -> str:
    if content:
        head = content[:512]
        if isinstance(head, str):
            head = head.encode("utf-8")
        head = head.lstrip()
        if head.startswith((b"<!doctype", b"<html", b"<?xml", b"<")):
            return "HTML"
        for magic in _MAGIC_FILE_PREFIXES:
            if head.startswith(magic):
                return "FILE"
    mime = (content_type or "").lower().split(";")[0].strip()
    if mime.startswith("text/html") or mime.startswith("application/xhtml"):
        return "HTML"
    if mime and not mime.startswith(("text/", "application/json", "application/xml")):
        return "FILE"
    ext = Path(urlparse(url).path).suffix.lower()
    return "FILE" if ext in _FILE_EXTENSIONS else "HTML"