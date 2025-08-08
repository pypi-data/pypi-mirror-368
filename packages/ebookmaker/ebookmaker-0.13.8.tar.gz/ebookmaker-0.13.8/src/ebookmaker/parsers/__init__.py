#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: UTF8 -*-

"""

Parser Package

Copyright 2009 by Marcello Perathoner
Copyright 2025 by Project Gutenberg

Distributable under the GNU General Public License Version 3 or newer.

"""

from __future__ import unicode_literals

import re
import os
import cchardet
import copy

import six
from six.moves import urllib
import unicodedata

import lxml.html
from lxml import etree
from lxml.builder import ElementMaker

import libgutenberg.GutenbergGlobals as gg
from libgutenberg.GutenbergGlobals import NS, xpath
from libgutenberg.MediaTypes import mediatypes as mt
from libgutenberg.Logger import info, debug, warning, error

from ebookmaker.CommonCode import Options

options = Options()

BROKEN = 'resource://ebookmaker.parsers/broken.png'

RE_GUTENBERG = re.compile(r'Project Gutenberg', re.I)
RE_AUTHOR = re.compile(r"^Author:\s+(.+)$", re.I | re.M)
RE_TITLE = re.compile(r"^Title:\s+(.+)$", re.I | re.M)
RE_LANGUAGE = re.compile(r"^Language:\s+(.+)$", re.I | re.M)
# Release Date: September 5, 2009 [EBook #29915]
RE_RELEASEDATE = re.compile(r"^(Release|Posting)\s+Date:\s+(.+)\[", re.I | re.M)
RE_EBOOKNO = re.compile(r'\[E(?:Book|Text) #(\d+)\]', re.I | re.M)

REB_XML_CHARSET = re.compile(br'^<\?xml.*encoding\s*=\s*["\']([^"\'\s]+)', re.I)
RE_HTML_CHARSET = re.compile(r';\s*charset\s*=\s*([^"\'\s]+)', re.I)
REB_HTML_CHARSET = re.compile(br';\s*charset\s*=\s*([^"\'\s]+)', re.I)
REB_PG_CHARSET = re.compile(br"^Character Set Encoding:\s+([-\w\d]+)\s*$", re.I | re.M)


# XML 1.1 RestrictedChars
# [#x1-#x8] | [#xB-#xC] | [#xE-#x1F] | [#x7F-#x84] | [#x86-#x9F]
RE_RESTRICTED = re.compile('[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]')

XML_NAMESTARTCHAR = 'A-Z_a-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02ff' \
                    '\u0370-\u037d\u037f-\u1fff\u200c-\u200d\u2070-\u218f' \
                    '\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd'
                    # u'\U00010000-\U000effff'
XML_NAMECHAR = XML_NAMESTARTCHAR + '.0-9\u00b7\u0300-\u036f\u203f-\u2040-'

RE_XML_NAME = re.compile('^[%s][%s]*$' % (XML_NAMESTARTCHAR, XML_NAMECHAR))

URI_MARK_CHARS = "-_.!~*'()"
URI_RESERVED_CHARS = ';/?:@&=+$,'

RE_URI_FRAGMENT = re.compile('[' + URI_MARK_CHARS + URI_RESERVED_CHARS + '%A-Za-z0-9]+')
RE_NO_WS = re.compile(r'^\S.*')

# all bogus encoding names used in PG go in here
BOGUS_CHARSET_NAMES = {'iso-latin-1': 'iso-8859-1',
                       'big5': 'big5hkscs',
                       'big-5': 'big5hkscs',

                       # python has bogus codec name
                       'macintosh': 'mac_roman',
                       }
COREATTRS = ["class", "dir", "id", "lang", "style", "title"]

# legal on A but not GLOBAL
A_NOT_GLOBAL = [
    'download',
    'href',
    'hreflang',
    'ping',
    'referrerpolicy',
    'rel',
    'target',
    'type',
]

STYLE_LINK = '<link href="pgepub.css" rel="stylesheet"/>'

# note: title is prequoted
IMAGE_WRAPPER = """<?xml version="1.0"?>{doctype}
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title>{title}</title>
    {style}
  </head>
  <body>
    <div style="text-align: center">
      <img src="{src}" alt="" class="{wrapper_class}" />
      {backlink}
    </div>
  </body>
</html>"""

RE_PG_OLD_HOST = re.compile(r'http://(www\.)?gutenberg\.(org|net)/')
RE_PG_HTML_URL = re.compile(r'([^a-zA-Z0-9./?=_%:-])https://(www\.)?gutenberg\.org/files/(\d+)/\3-h/\3-h\.htm([^a-zA-Z0-9./?=_%:-])')
REPL_PG_HTML5_URL = r'\g<1>https://www.gutenberg.org/cache/epub/\g<3>/pg\g<3>-images.html\g<4>'
# exported

em = ElementMaker(makeelement=lxml.html.xhtml_parser.makeelement,
                  namespace=str(NS.xhtml),
                  nsmap={None: str(NS.xhtml)})

def webify_url(url):
    """ make the url for a parser, accounting for platform """
    if re.search(r'^https?://', url):
        return url
    if url.startswith('file:'):
        return url
    if url.startswith('resource:'):
        return url
    if re.search(r'^[a-zA-z]:', url):
        return 'file:///' + url.replace(os.path.sep, '/')
    url = os.path.abspath(url).replace(os.path.sep, '/')
    if url.startswith('/'):
        url = url[1:]
    return 'file:///' + url

def update_urls(text):
    text = RE_PG_OLD_HOST.sub('https://www.gutenberg.org/', text)
    return RE_PG_HTML_URL.sub(REPL_PG_HTML5_URL, text)

class ParserAttributes(object): # pylint: disable=too-few-public-methods
    """ Object to hold attributes for the lifetime of a parser.

    Typical attributes held here would be:
      - url
      - orig_url
      - mediatype
      - orig_mediatype
      - referrer
      - id

    mediatype is not necessarily the same as orig_mediatype,
    because parsers may convert between input and output, eg.
    reST to xhtml.

    """

    def __init__(self):
        self.url = None
        self.orig_url = None
        self.mediatype = None
        self.orig_mediatype = None
        self.id = None
        self.rel = set()
        self.referrer = None
        self.title = None


    def update(self, more_attribs):
        for k, v in vars(more_attribs).items():
            if v:
                setattr(self, k, v)


    def get(self, name, default=None):
        return getattr(self, name, default)

    def __str__(self):
        a = []
        for k, v in vars(self).items():
            a.append('%s=%s' % (k, v))
        return '\n'.join(a)


class ParserBase(object):
    """ Base class for more specialized parsers. """

    def __init__(self, attribs=None):
        self.attribs = attribs or ParserAttributes()
        self.attribs.mediatype = self.attribs.orig_mediatype
        self.fp = None
        self.buffer = None
        self.unicode_buffer = None


    def reset(self):
        """ Make the parser safe for re-use.

        This method is called before parser is reused. 

        """
        pass




    def pre_parse(self):
        """ Do a lightweight parse, that allows iterlinks () to succeed.

        Spider.py needs to use iterlinks () to grab dependencies, but
        does not need a full parse. If a lightweight parse doesn't
        make sense, you may also do a full parse here and save the
        result.

        """
        pass


    def parse(self):
        """ Do a full parse.

        When this gets called, a pre_parse has already been done,
        so you might safely reuse any cached results.

        """

        pass


    def get_charset_from_meta(self): # pylint: disable=R0201
        """ Parse header metadata for charset.

        Header metadata can be either of:

          - html metadata
          - rst enconding comment
          - pg header charset line

        Override this as required.

        """

        return None


    def guess_charset_from_body(self):
        """ Guess charset from text. """

        result = cchardet.detect(self.bytes_content())
        charset = result.get('encoding')
        if charset:
            debug('Got charset %s from text sniffing' % charset)
            return charset
        return None


    def bytes_content(self):
        """ Get document content as raw bytes. """

        if self.buffer is None:
            if self.fp is None:
                return b''
            try:
                debug("Fetching %s ..." % self.attribs.url)
                self.buffer = self.fp.read()
                self.fp.close()
            except IOError as what:
                error(what)

        return self.buffer


    def unicode_content(self):
        """ Get document content as unicode string. """

        if self.unicode_buffer is None:
            data = (self.decode(self.get_charset_from_meta()) or
                    self.decode(self.guess_charset_from_body()) or
                    self.decode('utf-8') or
                    self.decode('windows-1252'))

            if not data:
                if data == '':
                    info('Continuing parse despite missing file')
                    self.unicode_buffer = ''
                else:
                    raise UnicodeError("Text in Klingon encoding ... giving up.")
            # NFC
            data = unicodedata.normalize('NFC', data)
            debug('NFC normalized data')

            # normalize line-endings
            if '\r' in data or '\u2028' in data:
                data = '\n'.join(data.splitlines())
            data = update_urls(data)

            self.unicode_buffer = data

        return self.unicode_buffer


    def decode(self, charset):
        """ Try to decode document contents to unicode. """
        if charset is None:
            return None

        charset = charset.lower().strip()

        if charset in BOGUS_CHARSET_NAMES:
            charset = BOGUS_CHARSET_NAMES[charset]

        if charset == 'utf-8':
            charset = 'utf_8_sig'

        try:
            debug("Trying to decode document with charset %s ..." % charset)
            buffer = self.bytes_content()
            buffer = REB_PG_CHARSET.sub(b'', buffer)
            buffer = buffer.decode(charset)
            return buffer
        except LookupError as what:
            # unknown charset,
            error("Invalid charset name: %s (%s)" % (charset, what))
        except UnicodeError as what:
            # mis-stated charset, did not decode
            error(f"Text in {self.attribs.url} not in charset {charset} ({what})")
        return None


    def mediatype(self):
        """ Return parser output mediatype. Helper function. """
        if self.attribs.mediatype:
            return self.attribs.mediatype
        return None


    # Links are found in HTMLParserBase and CSSParser. These methods
    # are overwritten there.

    def iterlinks(self): # pylint: disable=R0201
        """ Return all links in document.

        returns a list of url, dict
        dict may contain any of: tag, id, rel, type.

        """

        return []


    def rewrite_links(self, dummy_f): # pylint: disable=R0201
        """ Rewrite all links using the function f. """
        return


    def remap_links(self, dummy_url_map): # pylint: disable=R0201
        """ Rewrite all links using the dictionary url_map. """
        return

class TxtParser(ParserBase):
    """ Base class for text files we don't want to convert.
    """

    def __init__(self, attribs=None):
        ParserBase.__init__(self, attribs)
        self.attribs.mediatype = mt.txt

    def serialize(self):
        return bytes(self.unicode_content(), 'utf8')

class HTMLParserBase(ParserBase):
    """ Base class for more HTMLish parsers.

    (HTMLParser, GutenbergTextParser)

    """

    def __init__(self, attribs=None):
        ParserBase.__init__(self, attribs)
        self.attribs.mediatype = mt.xhtml
        self.xhtml = None
        self._xhtml = None


    def reset(self):
        if self._xhtml is not None:
            self.xhtml = self._xhtml
            self._xhtml = None


    @staticmethod
    def add_class(elem, class_):
        """ Add a class to html element. """
        classes = elem.get('class', '').split()
        classes.append(class_)
        elem.set('class', ' '.join(classes))


    def get_charset_from_meta(self):
        """ Parse text for hints about charset. """

        charset = None
        html = self.bytes_content()

        match = REB_XML_CHARSET.search(html)
        if match:
            charset = match.group(1).decode('ascii')
            debug('Got charset %s from xml declaration' % charset)
        else:
            match = REB_HTML_CHARSET.search(html)
            if match:
                charset = match.group(1).decode('ascii')
                debug('Got charset %s from html meta' % charset)

        return charset


    def iterlinks(self):
        """ Return all links in document. """

        # To keep an image even in non-image build specify
        # class="x-ebookmaker-important"

        keeps = xpath(self.xhtml, "//img[contains (@class, 'x-ebookmaker-important')]")
        for keep in keeps:
            keep.set('rel', 'important')

        # iterate links

        for (elem, dummy_attribute, url, dummy_pos) in self.xhtml.iterlinks():
            yield url, elem


    def rewrite_links(self, f):
        """ Rewrite all links using the function f. """
        self.xhtml.rewrite_links(f)


    def remap_links(self, url_map):
        """ Rewrite all links using the dictionary url_map. """
        def f(url):
            """ Remap function """
            ur, frag = urllib.parse.urldefrag(url)
            if ur in url_map:
                debug("Rewriting redirected url: %s to %s" % (ur, url_map[ur]))
                ur = url_map[ur]
            return "%s#%s" % (ur, frag) if frag else ur

        self.rewrite_links(f)


    @staticmethod
    def strip_links(xhtml, manifest):
        """ Strip all links to urls not in manifest.

        This includes  <link href> and <img src> and, if strip_links is set, <a href>.
        Assume links and urls are already made absolute.

        """
        if options.strip_links:
            replacements = 0
            for link in xpath(xhtml, '//xhtml:a[@href]'):
                href = urllib.parse.urldefrag(link.get('href'))[0]
                if href not in manifest:
                    replacements += 1
                    del link.attrib['href']
            if replacements:
                debug(f"stripped {replacements} <a>s for href not in manifest.")

        replacements = 0
        for link in xpath(xhtml, '//xhtml:link[@href]'):
            href = link.get('href')
            if href not in manifest:
                replacements += 1
                link.drop_tree()
        if replacements:
            debug(f"stripped {replacements} <link>s for href not in manifest.")

        replacements = 0
        for image in xpath(xhtml, '//xhtml:*[@src]'):
            src = image.get('src')
            if src not in manifest:
                replacements += 1
                image.tag = NS.xhtml.span
                image.text = image.get('alt', '')
                for attr  in image.attrib:
                    if attr not in COREATTRS:
                        del image.attrib[attr]
        if replacements:
            debug(f"stripped {replacements} <img>s for src not in manifest.")


    def make_toc(self, xhtml):
        """ Build a TOC from HTML headers.

        Return a list of tuples (url, text, depth).

        Page numbers are also inserted because DTBook NCX needs the
        play_order to be sequential.

        """

        def id_generator(i=0):
            """ Generate an id for the TOC to link to. """
            while True:
                yield 'pgepubid%05d' % i
                i += 1

        def get_header_text(header):
            """ clean header text
                also, replace breaks with whitespace. tidy used to put whitespace around <br>
                elements. PPs relied on this behavior, so we're stuck. """
            for br in xpath(header, '//xhtml:br'):
                if RE_NO_WS.match(str(br.tail)):
                    br.tail = '\n' + str(br.tail) if br.tail else '\n'

            text = gg.normalize(etree.tostring(header,
                                               method="text",
                                               encoding=six.text_type,
                                               with_tail=False))

            return header.get('title', text).strip()

        idg = id_generator()

        def get_id(elem):
            """ Get the id of the element or generate and set one. """
            if not elem.get('id'):
                elem.set('id', six.next(idg))
            return elem.get('id')

        toc = []

        for header in xpath(
                xhtml,
                '//xhtml:h1|//xhtml:h2|//xhtml:h3|//xhtml:h4|'
                # DP page number
                '//xhtml:*[contains (@class, "pageno")]|'
                # DocUtils contents header
                '//xhtml:p[contains (@class, "topic-title")]'
            ):

            previous = header.getprevious()
            if previous is not None and previous.tag == header.tag:
                # consecutive headers get combined
                continue

            text = get_header_text(header)

            if not text:
                # so <h2 title=""> may be used to suppress TOC entry
                continue

            if header.get('class', '').find('pageno') > -1:
                toc.append(["%s#%s" % (self.attribs.url, get_id(header)), text, -1])
            else:
                # header
                if ((text.lower().startswith('by ')
                     or text.lower() == ('by'))
                        and 'x-ebookmaker-important' not in header.get('class', '')):
                    # common error in PG: <h2>by Lewis Carroll</h2> should
                    # yield no TOC entry
                    warning(f'dropping by-heading in {self.attribs.url}: {text.lower()}')
                    warning('use x-ebookmaker-important class if this heading should be in TOC')
                    continue

                try:
                    depth = int(header.tag[-1:])
                except ValueError:
                    depth = 2 # avoid top level

                #join consecutive headers
                next = header.getnext()
                while next is not None and next.tag == header.tag:
                    text = (text + ' ' + get_header_text(next)).strip()
                    next = next.getnext()

                # if <h*> is first element of a <div> use <div> instead
                parent = header.getparent()
                if (parent.tag == NS.xhtml.div and
                        parent[0] == header and
                        parent.text and
                        parent.text.strip() == ''):
                    header = parent

                toc.append(["%s#%s" % (self.attribs.url, get_id(header)), text, depth])

        return toc


    def serialize(self):
        """ Serialize to string. """
        if self.attribs.url.endswith('.xhtml'):
            # epub3
            doctype = ""
        else:
            # epub2
            doctype=gg.XHTML_DOCTYPE
        return etree.tostring(self.xhtml,
                              doctype=doctype,
                              xml_declaration=True,
                              encoding='utf-8',
                              pretty_print=True)
