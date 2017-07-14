#!/usr/bin/env python
# encoding: utf-8
###############################################################################
#                                                                             #
#    PyMICE library                                                           #
#                                                                             #
#    Copyright (C) 2017 Jakub M. Dzik a.k.a. Kowalski (Laboratory of          #
#    Neuroinformatics; Nencki Institute of Experimental Biology of Polish     #
#    Academy of Sciences)                                                     #
#                                                                             #
#    This software is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This software is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this software.  If not, see http://www.gnu.org/licenses/.     #
#                                                                             #
###############################################################################

from ._Version import __version__, __RRID__
import sys

if sys.version_info.major == 3:
    from functools import reduce

def _authorsBibliographyAPA6(authors, **kwargs):
    formatted = [_authorBibliographyAPA6(*a) for a in authors]
    return u', '.join(formatted[:-1] + [u'&\xa0' + formatted[-1]])

def _authorBibliographyAPA6(familyName, *names):
    return u'{},\u00a0{}'.format(familyName, u'\xa0'.join(n[0] + '.' for n in names))

class Citation(object):
    _DEFAULT_META = {'rrid': __RRID__,
                    'authors': [('Dzik', 'Jakub', 'Mateusz'),
                                (u'Łęski', 'Szymon'),
                                (u'Puścian', 'Alicja'),
                                ],
                     }
    _META = {'1.1.1': {'doi': '10.5281/zenodo.557087',
                      'year': 2017,
                      'month': 'April',
                      'day': 24,
                       },
            '1.1.0': {'doi': '10.5281/zenodo.200648',
                      'year': 2016,
                      'month': 'December',
                      'day': 13,
                      },
            '1.0.0': {'doi': '10.5281/zenodo.51092',
                      'year': 2016,
                      'month': 'May',
                      'day': 6,
                      },
             '0.2.5': {'doi': '10.5281/zenodo.49550',
                      'year': 2016,
                      'month': 'April',
                      'day': 11,
                      },
             '0.2.4': {'doi': '10.5281/zenodo.47305',
                      'year': 2016,
                      'month': 'January',
                      'day': 30,
                      },
             '0.2.3': {'doi': '10.5281/zenodo.47259',
                      'year': 2016,
                      'month': 'January',
                      'day': 30,
                      },
             }

    _PAPER_META = {
        'authors': [('Dzik', 'Jakub', 'Mateusz'),
                    (u'Puścian', 'Alicja'),
                    ('Mijakowska', 'Zofia'),
                    ('Radwanska', 'Kasia'),
                    (u'Łęski', 'Szymon'),
                    ],
        'title': '{PyMICE}: A {Python} library for analysis of {IntelliCage} data',
        'year': 2017,
        'day': 22,
        'month': 'June',
        'journal': 'Behavior Research Methods',
        'journalAbbreviationNLM': 'Behav Res Methods',
        'doi': '10.3758/s13428-017-0907-5',
        'issn': '1554-3528',
        'abstract': '{IntelliCage} is an automated system for recording the '
                    'behavior of a group of mice housed together. It produces '
                    'rich, detailed behavioral data calling for new methods '
                    'and software for their analysis. Here we present {PyMICE},'
                    ' a free and open-source library for analysis of '
                    '{IntelliCage} data in the {Python} programming language. '
                    'We describe the design and demonstrate the use of the '
                    'library through a series of examples. {PyMICE} provides '
                    'easy and intuitive access to {IntelliCage} data, and thus '
                    'facilitates the possibility of using numerous other '
                    '{Python} scientific libraries to form a complete data '
                    'analysis workflow.'
        }


    _DEFAULT_STYLE = 'apa6'
    _DEFAULT_MARKDOWN = {'apa6': 'txt',
                         'bibtex': 'latex',
                         'pymice': 'txt',
                         'vancouver': 'txt',
                         }
    _SOFTWARE_PATTERNS = {
        'apa6': ({'txt': u"{authors} ({date}). {title} [{note}]{doi}",
                  'latex': u"\\bibitem{{pymice{version}}} {authors} ({date}). {title} [{note}]{doi}",
                  },
                 [('authors', _authorsBibliographyAPA6),
                  ('title', u"PyMICE (v.\xa0{__version__})".format),
                  ('title', u"PyMICE".format),
                  ('date', u'{year},\xa0{month}'.format),
                  ('date', 'n.d.'.format),
                  ('doi', u'. doi:\xa0{doi}'.format),
                  ('doi', ''.format),
                  ('note', 'computer software; {rrid}'.format),
                  ('version', '{__version__}'.format),
                  ('version', ''.format),
                  ]),
        'bibtex': (u"@Misc{{pymice{version},\nTitle = {{{{{title}}}}}{note},\nAuthor = {{{authors}}}{date}{doi}\n}}\n",
                   [('authors', lambda **kwargs: ' and '.join(u'{}, {}'.format(a[0], ' '.join(a[1:])) for a in kwargs['authors'])),
                    ('title', u"PyMICE (v.\xa0{__version__})".format),
                    ('title', u"PyMICE".format),
                    ('date', ",\nYear = {{{year}}},\nMonth = {{{month}}},\nDay = {{{day}}}".format),
                    ('date', "".format),
                    ('doi', ",\nDoi = {{{doi}}}".format),
                    ('doi', "".format),
                    ('note', ',\nNote = {{computer software; {rrid}}}'.format),
                    ('version', '{__version__}'.format),
                    ('version', ''.format),
                    ]),
        'pymice': (u"Dzik\xa0J.\xa0M., Łęski\xa0S., Puścian\xa0A. {date}\"PyMICE\" {version}{doi}",
                   [('date', u'({month}\xa0{day},\xa0{year}) '.format),
                    ('date', ''.format),
                    ('version', u'computer software (v.\xa0{__version__}; {rrid})'.format),
                    ('version', u'computer software ({rrid})'.format),
                    ('doi', u' doi:\xa0{doi}'.format),
                    ('doi', ''.format),
                    ]),
        'vancouver': (u"Dzik\xa0JM, Łęski\xa0S, Puścian\xa0A. PyMICE [computer software].{version} Warsaw: Nencki Institute{date}.{doi}",
                      [('version', u' Version {__version__}.'.format),
                       ('version', u''.format),
                       ('date', '; {year}'.format),
                       ('date', ''.format),
                       ('doi', u' DOI:\xa0{doi}'.format),
                       ('doi', ''.format),
                       ]),
    }
    _CITE_SOFTWARE_PATTERNS = {
        'apa6': ({'txt': u"PyMICE\xa0(Dzik, Puścian, Mijakowska, Radwanska, &\xa0Łęski, 2017{version}{authors}, {date})",
                  'latex': u"\\emph{{PyMICE}}~\\cite{{dzik2017pm{version_latex}}}",
                  },
                 [('authors', lambda **x: ', '.join([a[0] for a in x['authors'][:-1]] + [u'&\xa0' + x['authors'][-1][0]])),
                  ('date', '{year}'.format),
                  ('date', 'n.d.'.format),
                  ('version', u') v.\xa0{__version__}\xa0('.format),
                  ('version', '; '.format),
                  ('version_latex', '}} v.~{__version__}~\\cite{{pymice{__version__}'.format),
                  ('version_latex', ',pymice'.format),
                  ]),
        'bibtex': (u"\\emph{{PyMICE}}~\\cite{{dzik2017pm{version}}}",
                   [('version', '}} v.~{__version__}~\\cite{{pymice{__version__}'.format),
                    ('version', ',pymice'.format),
                   ]),
        'pymice': (u"PyMICE\xa0(Dzik, Puścian, et\xa0al. 2017{version}Dzik, Łęski, &\xa0Puścian{date})",
                   [('version', u') v.\xa0{__version__}\xa0('.format),
                    ('version', '; '.format),
                    ('date', ' {year}'.format),
                    ('date', ''.format),
                    ]),
        'vancouver': (u"PyMICE\xa0({rrid})\xa0[1{version}2]",
                      [('rrid', '{rrid}'.format),
                       ('version', u'] v.\xa0{__version__}\xa0['.format),
                       ('version', ','.format),
                       ]),
    }

    _MARKDOWN_ESCAPE = {
                       'latex': [('_', '\\_'),
                                 (u'\xa0', '~'),
                                 ('<em>', '\\emph{'),
                                 ('</em>', '}'),
                                 ],
                       'html': [('{', ''),
                                ('}', ''),
                                ('&', '&amp;'),
                                (u'\xa0', '&nbsp;'),
                                ],
                       'md': [('{', ''),
                              ('}', ''),
                              ('_', '\\_'),
                              ('<em>', '_'),
                              ('</em>', '_'),
                              ],
                       'rst': [('{', ''),
                               ('}', ''),
                               ('_', '\\_'),
                               ('<em>', '*'),
                               ('</em>', '*'),
                               ],
                       'txt': [('{', ''),
                               ('}', ''),
                               ('<em>', ''),
                               ('</em>', ''),
                               ]
                       }

    _PAPER_PATTERNS = {'apa6': ({'txt': u"{authors} ({date}). {title}. {journal}{doi}",
                                'latex': u"\\bibitem{{dzik2017pm}} {authors} ({date}). {title}. {journal}{doi}",
                                 },
                                [('authors', _authorsBibliographyAPA6),
                                ('date', u'{year}'.format),
                                ('title', u'{title}'.format),
                                ('journal', '<em>{journal}</em>'.format),
                                ('doi', u'. doi:\xa0{doi}'.format),
                                ]),
                       'bibtex': (u"@Article{{dzik2017pm{title},\nAuthor = {{{authors}}}{date}{journal}{doi}{issn}{url}{abstract}\n}}\n",
                                 [('authors', lambda **kwargs: ' and '.join(u'{}, {}'.format(a[0], ' '.join(a[1:])) for a in kwargs['authors'])),
                                  ('title', u",\nTitle = {{{title}}}".format),
                                  ('date', ",\nYear = {{{year}}},\nMonth = {{{month}}},\nDay = {{{day}}}".format),
                                  ('journal', ",\nJournal = {{{journal}}}".format),
                                  ('doi', ",\nDoi = {{{doi}}}".format),
                                  ('issn', ",\nIssn = {{{issn}}}".format),
                                  ('url', ",\nUrl = {{http://dx.doi.org/{doi}}}".format),
                                  ('abstract', ",\nAbstract = {{{abstract}}}".format),
                                  ]),
                       'pymice': (u"{authors} ({date}) \"{title}\" {journal} {doi}",
                                 [('authors', lambda **kwargs: ', '.join(u'\xa0'.join([a[0]] + [x[0] + '.' for x in a[1:]]) for a in kwargs['authors'])),
                                  ('date', u'{month}\xa0{day},\xa0{year}'.format),
                                  ('title', u'{title}'.format),
                                  ('journal', '{journal}'.format),
                                  ('doi', u'doi:\xa0{doi}'.format),
                                  ]),
                       'vancouver': (u"{authors}. {title}. {journal}. {date}. {doi}",
                                     [('authors', lambda **kwargs: ', '.join(a[0] + u'\xa0' + ''.join(x[0] for x in a[1:]) for a in kwargs['authors'])),
                                      ('date', u'{year}'.format),
                                      ('title', u'{title}'.format),
                                      ('journal', '{journalAbbreviationNLM}'.format),
                                      ('doi', u'DOI:\xa0{doi}'.format),
                                      ]),
    }

    def __init__(self, style=None, markdown=None, version=__version__,
                       maxLineWidth=80):
        self._version = version
        self._setStyle(style)
        self._markdown = markdown
        self._maxLineWidth = maxLineWidth

    def _setStyle(self, style):
        self._style = style if style is not None else self._DEFAULT_STYLE

    def referencePaper(self, style=None):
        if style is None:
            style = self._style

        pattern, sections = self._getFormatters(self._PAPER_PATTERNS,
                                                style)
        return self._fold(self._applyMarkdown(self._formatMeta(pattern,
                                                               sections,
                                                               self._PAPER_META),
                                              self._getMarkdown(style, self._markdown)))

    @property
    def PAPER(self):
        return self.referencePaper()

    def _fold(self, string):
        maxWidth = self._maxLineWidth
        if maxWidth is None:
            return string

        indentWidth = 4

        words = [w for w in string.split(' ') if w != '']
        lines = [words[0]]

        for w in words[1:]:
            if len(w) + len(lines[-1]) < maxWidth:
                lines[-1] += ' ' + w
            else:
                lines.append(' ' * indentWidth + w)

        return '\n'.join(lines)

    def _formatMeta(self, template, sections, meta):
        return self._format(template,
                            self._sections(meta,
                                           reversed(sections)))

    def _format(self, pattern, sections):
        return pattern.format(**dict(sections))

    def referenceSoftware(self, style=None, **kwargs):
        if style is None:
            style = self._style

        version = kwargs.get('version',
                             self._version)

        pattern, sections = self._getFormatters(self._SOFTWARE_PATTERNS,
                                                style)
        return self._fold(self._applyMarkdown(self._formatMeta(pattern,
                                                    sections,
                                                    self._getMeta(version)),
                                   self._getMarkdown(style,
                                                     self._markdown)))

    @property
    def SOFTWARE(self):
        return self.referenceSoftware()

    def cite(self, version, style):
        pattern, sections = self._getFormatters(self._CITE_SOFTWARE_PATTERNS,
                                                style)
        formatted = self._formatMeta(pattern,
                                     sections,
                                     self._getMeta(version))
        return self._applyMarkdown(formatted,
                                   self._getMarkdown(style,
                                                     self._markdown))

    def _applyMarkdown(self, string, markdown):
        return reduce(lambda s, substitution: s.replace(*substitution),
                      self._MARKDOWN_ESCAPE[markdown],
                      string)

    def _getMarkdown(self, style, markdown):
        if markdown is not None: return markdown

        try:
            return self._DEFAULT_MARKDOWN[style]
        except KeyError:
            pass #return self._DEFAULT_MARKDOWN[self._DEFAULT_STYLE]

    def _getFormatters(self, formatters, style):
        pattern, sections = formatters[style]
        try:
            pattern = pattern[self._markdown]
        except TypeError:
            pass
        except KeyError:
            pattern = pattern[self._DEFAULT_MARKDOWN[style]]

        return pattern, sections

    def _getMeta(self, version):
        meta = self._DEFAULT_META.copy()
        if version is not None:
            meta['__version__'] = version

        try:
            meta.update(self._META[version])
        except KeyError:
            pass

        return meta

    def _sections(self, meta, formatters):
        for key, formatter in formatters:
            try:
                yield key, formatter(**meta)
            except KeyError:
                pass

    def _str(self):
        return self.cite(self._version, self._style)

    if sys.version_info.major < 3:
        def __unicode__(self):
            return self._str()

        def __str__(self):
            return self._str().encode('utf-8')

    else:
        def __str__(self):
            return self._str()

reference = Citation()