import re
import requests
from StringIO import StringIO
from urlparse import urlparse, urlunparse, urljoin
from tldextract import extract
from bs4 import BeautifulSoup
from PIL import Image


def og_data_for_url(url):
    requester = OGDataRequester(url)
    return requester()


OG_TAGS = ["url",
           "title",
           "site_name",
           "description",
           "image"]

OG_PAGE_CHECK_TIMEOUT = 5
OG_IMAGE_CHECK_TIMEOUT = 5
OG_FAVICON_CHECK_TIMEOUT = 2

URL_SCHEMA_PATTERN = re.compile('^[hH][tT][tT][pP][sS]?://.*$')
URL_DEFAULT_SCHEME = 'http'


class OGDataRequester(object):
    """Provides Open Graph data for a url
    """

    def __init__(self, url):
        self.url = self._ensure_url_http_scheme(url)

    def __call__(self):
        data = {}
        headers = {'User-Agent': 'irisbot 1.0'}
        page = requests.get(self.url,
                            timeout=OG_PAGE_CHECK_TIMEOUT,
                            headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        soup.prettify()
        for tag_name in OG_TAGS:
            tag_content = self._get_tag_content(soup, 'og:' + tag_name)
            if tag_content:
                data[tag_name] = tag_content
        url = data.get('url', self.url)
        if data:
            favicon = self._get_favicon(soup, url)
            if favicon is not None:
                data['favicon'] = favicon
        img = data.get('image')
        if img:
            image_data = self._get_image_data(img, url)
            if image_data:
                data['image'] = image_data['url']
                data['image_data'] = {
                    'width': image_data['width'],
                    'height': image_data['height']
                }
            else:
                del data['image']
        if data:
            if 'url' in data:
                data['url'] = self._ensure_url_http_scheme(
                    data['url'])
            else:
                data['url'] = url
        return data

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
        parsed_img = urlparse(img)
        if not extract(img).suffix:
            if url:
                parsed_url = urlparse(url)
                if parsed_img.path.startswith("/"):
                    url = urlunparse((parsed_url.scheme,
                                      parsed_url.netloc,
                                      "",
                                      "",
                                      "",
                                      ""))
                elif not url.endswith("/"):
                    url += "/"
                return urljoin(url, img)
            else:
                return ""
        else:
            if not parsed_img.scheme:
                if url and urlparse(url).scheme:
                    img = self._ensure_url_http_scheme(img,
                                                       urlparse(url).scheme)
                else:
                    img = self._ensure_url_http_scheme(img)
        return img

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
                            'url': url,
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

    def _get_tag_content(self, soup, og_tag):
        """Get value of og tag
        """
        tag = soup.findAll(attrs={"property": og_tag})
        if len(tag) > 0:
            return tag[0].get('content')

    def _get_tags(self, soup, name, attrs):
        return soup.findAll(name, attrs=attrs)

    def _ensure_url_http_scheme(self, url, scheme=URL_DEFAULT_SCHEME):
        if not URL_SCHEMA_PATTERN.match(url):
            return "%s://%s" % (scheme, url)
        return url
