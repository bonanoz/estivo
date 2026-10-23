"""Test helpers shared by the redesign test contract (not a test module itself).

- ``parse(resp_or_html)`` builds a tiny DOM tree with the stdlib ``HTMLParser`` so
  tests can assert on elements/attributes/order instead of raw substrings.
- ``make_product(**kw)`` creates a ``Product`` with sane defaults; any extra
  model fields (``is_new``, ``is_bestseller``...) are passed through as-is, so a
  test that uses a not-yet-existing field fails loudly with ``TypeError``.
"""
import json
import re
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from shop.models import Product

VOID_TAGS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
    'param', 'source', 'track', 'wbr',
}


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.parent = parent
        self.children = []

    def __repr__(self):
        return f'<{self.tag} {self.attrs}>'

    # --- traversal -------------------------------------------------------
    def iter(self):
        """All descendant elements in document order (self excluded)."""
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.iter()

    def iter_self(self):
        yield self
        yield from self.iter()

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    # --- attributes ------------------------------------------------------
    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def has_attr(self, name):
        return name in self.attrs

    def classes(self):
        return self.attrs.get('class', '').split()

    def has_class(self, cls):
        return cls in self.classes()

    @property
    def text(self):
        parts = []
        for child in self.children:
            parts.append(child.text if isinstance(child, Node) else child)
        return ''.join(parts)

    # --- matching --------------------------------------------------------
    def matches(self, tag=None, attrs=None, cls=None, pred=None):
        if tag is not None and self.tag != tag:
            return False
        if cls is not None and not self.has_class(cls):
            return False
        for key, value in (attrs or {}).items():
            if key not in self.attrs:
                return False
            if value is not True and self.attrs[key] != value:
                return False
        if pred is not None and not pred(self):
            return False
        return True

    def find_all(self, tag=None, attrs=None, cls=None, pred=None):
        return [n for n in self.iter() if n.matches(tag, attrs, cls, pred)]

    def find(self, tag=None, attrs=None, cls=None, pred=None):
        for n in self.iter():
            if n.matches(tag, attrs, cls, pred):
                return n
        return None

    def closest(self, tag=None, attrs=None, cls=None, pred=None):
        """Self or nearest ancestor matching the criteria."""
        if self.matches(tag, attrs, cls, pred):
            return self
        for anc in self.ancestors():
            if anc.matches(tag, attrs, cls, pred):
                return anc
        return None

    def get_by_id(self, element_id):
        return self.find(attrs={'id': element_id})


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: ('' if v is None else v) for k, v in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, {k: ('' if v is None else v) for k, v in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def parse(resp_or_html):
    if isinstance(resp_or_html, (bytes, str)):
        html = resp_or_html
    else:
        html = resp_or_html.content
    if isinstance(html, bytes):
        html = html.decode('utf-8')
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    return builder.root


# --- text helpers ---------------------------------------------------------

def squash(text):
    """Remove all whitespace (incl. NBSP / narrow NBSP) — for price checks like '42 000 ₽'."""
    return re.sub(r'[\s  ]+', '', text)


def norm_space(text):
    return re.sub(r'[\s  ]+', ' ', text).strip()


def has_number(text, number):
    """True if ``number`` occurs in ``text`` as a standalone number."""
    return re.search(rf'(?<![\d.,]){re.escape(str(number))}(?![\d])', text) is not None


def query(href):
    """Parsed query string of a URL/href: {'page': ['2'], ...}."""
    return parse_qs(urlsplit(href).query)


def path_of(href):
    return urlsplit(href).path


def product_hrefs(node):
    """Distinct paths of links to product pages under ``node``."""
    return {path_of(a.get('href')) for a in node.find_all('a', attrs={'href': True})
            if path_of(a.get('href')).startswith('/product/')}


def json_ld_objects(root):
    """All JSON-LD objects on the page, flattening lists and @graph."""
    result = []
    for script in root.find_all('script', attrs={'type': 'application/ld+json'}):
        data = json.loads(script.text)
        stack = data if isinstance(data, list) else [data]
        for obj in stack:
            if isinstance(obj, dict) and '@graph' in obj:
                result.extend(obj['@graph'])
            else:
                result.append(obj)
    return result


def product_card_for(root, product):
    """The ``.product-card`` element that links to ``product`` (or None)."""
    url = product.get_absolute_url()
    for card in root.find_all(cls='product-card'):
        if url in product_hrefs(card):
            return card
    return None


# --- factories ------------------------------------------------------------

_counter = {'n': 0}


def make_product(**kwargs):
    """Create a Product. Unknown kwargs go straight to the model (fail loudly if missing)."""
    _counter['n'] += 1
    n = _counter['n']
    kwargs.setdefault('name', f'Тестовый товар {n}')
    kwargs.setdefault('slug', f'test-product-{n}')
    kwargs.setdefault('description', 'Описание')
    kwargs.setdefault('price', 10000)
    colors = kwargs.pop('colors', None)
    product = Product.objects.create(**kwargs)
    if colors:
        product.available_colors.set(colors)
    return product
