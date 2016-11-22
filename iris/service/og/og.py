import re
import requests
import urllib
from StringIO import StringIO
from urlparse import urlparse, urlunparse, urljoin
from tldextract import extract
from bs4 import BeautifulSoup
from PIL import Image


HTTPS_PROXY_URL = None

OG_PAGE_CHECK_TIMEOUT = 5
OG_IMAGE_CHECK_TIMEOUT = 5
OG_FAVICON_CHECK_TIMEOUT = 2

URL_SCHEMA_PATTERN = re.compile('^[hH][tT][tT][pP][sS]?://.*$')
URL_DEFAULT_SCHEME = 'http'


def og_data_for_url(url):
    return OGDataRequester(url)


def normalize_url(url, scheme=URL_DEFAULT_SCHEME):
    if ((url and not urlparse(url).scheme)
        or not URL_SCHEMA_PATTERN.match(url)
       ):
        return "%s://%s" % (scheme, url)
    return url


class OGDataRequester(dict):
    """A dict like implementation for open graph data
    """

    FORCED_OBJECTS = ['image', 'video']

    def __init__(self, url):
        url = normalize_url(url)
        headers = {'User-Agent': 'irisbot 1.0'}
        page = requests.get(url,
                            timeout=OG_PAGE_CHECK_TIMEOUT,
                            headers=headers)
        doc = BeautifulSoup(page.content, "html.parser")
        self._extract_og(doc)
        self._extract_missing(doc)
        if not self:
            return
        if self.get('url'):
            self['url'] = normalize_url(self['url'])
        else:
            self['url'] = url
        url = self['url']
        favicon = self._get_favicon(doc, url)
        if favicon is not None:
            self['favicon'] = favicon
        img = self.get('image')
        if img:
            extract_size = 'width' not in img or 'height' not in img
            if extract_size:
                data = self['image']
                image_data = self._get_image_data(img['url'], url)
                if image_data:
                    data['url'] = image_data['url']
                    data['width'] = image_data['width']
                    data['height'] = image_data['height']
                else:
                    del self['image']

    def __setattr__(self, name, val):
        self[name] = val

    def __getattr__(self, name):
        return self[name]

    def _og_meta_tags(self, doc):
        for meta_tag in doc.findAll('meta'):
            if meta_tag.get('property', '').startswith('og:'):
                yield meta_tag

    def _get_favicon(self, soup, url):
        fq_favicon_url = None
        tags = self._get_tags(soup, 'link', {"rel": "icon"})
        if tags:
            href = tags[0].attrs.get('href')
            if href:
                fq_favicon_url = self._get_image_url(href, url)
        if fq_favicon_url is None:
            fq_favicon_url = self._get_image_url('/favicon.ico', url)
        if self._is_valid_image(fq_favicon_url):
            return fq_favicon_url

    def _get_image_url(self, img, url):
        if not extract(img).suffix:
            if not url:
                return ''
            parsed_img = urlparse(img)
            if parsed_img.path.startswith("/"):
                parsed_url = urlparse(url)
                url = urlunparse((parsed_url.scheme,
                                  parsed_url.netloc,
                                  "",
                                  "",
                                  "",
                                  ""))
            elif not url.endswith("/"):
                url += "/"
            return urljoin(url, img)
        return normalize_url(img)

    def _get_image_data(self, img, url):
        """Parse an image and return the image data (url, width, height).
        """
        url = self._get_image_url(img, url)
        if not url:
            return {}
        try:
            resp = requests.get(url,
                                timeout=OG_IMAGE_CHECK_TIMEOUT)
            c_type = resp.headers.get('content-type', '')
            if resp.status_code == 200 and c_type.startswith('image/'):
                try:
                    im = Image.open(StringIO(resp.content))
                    if (im.size):
                        return {
                            'url': self._https_proxy_url(url),
                            'width': im.size[0],
                            'height': im.size[1]
                        }
                except IOError:
                    pass
            return {}

        except requests.exceptions.RequestException:
            return {}

    def _is_valid_image(self, url):
        """Check if url is a valid image url
        """
        if not url:
            return False
        try:
            resp = requests.head(url, timeout=OG_FAVICON_CHECK_TIMEOUT)
            c_type = resp.headers.get('content-type', '')
            return (resp.status_code == 200 and c_type.startswith('image'))
        except requests.exceptions.RequestException:
            return False

    def _get_tags(self, soup, name, attrs):
        return soup.findAll(name, attrs=attrs)

    def _extract_og(self, doc):
        """Extract all open graph data into self
        """
        for og in self._og_meta_tags(doc):
            if not og.has_attr(u'content'):
                continue
            name_parts = og['property'][3:].split(':')
            name = name_parts[0]
            prop_name = None
            if len(name_parts) > 1:
                prop_name = name_parts[1]
            content = og['content']
            if prop_name is None:
                # don't overwrite existing properties
                if name not in self:
                    self[name] = content
            else:
                target = self.get(name, {})
                if not isinstance(target, dict):
                    target = {'url': target}
                elif name in self:
                    target = self[name]
                    if not isinstance(target, dict):
                        target = {
                            'url': self[name]
                        }
                self[name] = target
                # don't overwrite existing properties
                if prop_name not in target:
                    target[prop_name] = content
        for name in self.FORCED_OBJECTS:
            if name not in self:
                continue
            if not isinstance(self[name], dict):
                self[name] = {
                    'url': self[name]
                }

    REQUIRED_TAGS = [
        ('title', 'title_fallback'),
        ('description', 'description_fallback'),
    ]

    def _extract_missing(self, doc):
        """Extract missing og tags from other places

        """
        for required, handler in self.REQUIRED_TAGS:
            if required in self:
                continue
            getattr(self, handler)(doc)

    def title_fallback(self, doc):
        tag = doc.find('title')
        if tag is not None and tag.text:
            self['title'] = tag.text

    def description_fallback(self, doc):
        tag = doc.find('meta', {"name": "description"})
        if tag is not None:
            value = tag.get('content')
            if value:
                self['description'] = value

    def _https_proxy_url(self, url):
        if not HTTPS_PROXY_URL or not url.startswith('http:'):
            return url
        return HTTPS_PROXY_URL + '?' + urllib.urlencode({'url': url})


def includeme(config):
    global HTTPS_PROXY_URL
    settings = config.get_settings()
    HTTPS_PROXY_URL = settings.get('og.https_proxy_url', '')
