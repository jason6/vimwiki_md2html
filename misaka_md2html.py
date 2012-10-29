#!/usr/bin/env python3

"""Requirements:
python 3            for more robust unicode support
misaka              http://misaka.61924.nl/
jinja2              http://jinja.pocoo.org/

example installation (note the use of the python 3 specific pip):
    pip-3.2 install misaka Jinja2

This file must be executable:
    chmod 755 misaka_md2html.py

Required Vimwiki Settings in vimrc:
1.  custom_wiki2html should point to this file.
2.  path_html must be set
3.  syntax should equal 'markdown'
4.  css_name should point to the css file you want to use.  This has a default value of style.css so copying the provided style.css from autoload/vimwiki/ to your path_html should be sufficient to get started. 

"""

import os.path
import re
import argparse
from misaka import Markdown, HtmlRenderer, HtmlTocRenderer, SmartyPants, \
    EXT_NO_INTRA_EMPHASIS, EXT_TABLES, EXT_FENCED_CODE, EXT_AUTOLINK, \
    EXT_STRIKETHROUGH, EXT_SPACE_HEADERS, \
    EXT_SUPERSCRIPT, \
    HTML_SKIP_HTML, HTML_SKIP_STYLE, HTML_SKIP_IMAGES, HTML_SKIP_LINKS, \
    HTML_EXPAND_TABS, HTML_SAFELINK, HTML_TOC, HTML_HARD_WRAP, \
    HTML_USE_XHTML, HTML_ESCAPE, \
    HTML_SMARTYPANTS
from jinja2 import Template


# A basic default template to use until the vimwiki template settings are
# fully integrated.
template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                {% if cssfile %}
                    <link href="{{ cssfile }}" rel="stylesheet">
                {% endif %}
                {% if title %}
                    <title>{{ title }}</title>
                {% endif %}
            </head>
            <body>
                {% if title %}
                    <p id="title">{{ title }}</p>
                {% endif %}
                {% if toc_content %}
                    <p class="toc">Table of Contents</p>
                    {{ toc_content }}
                {% endif %}
                {{ main_content }}
            </body>
            </html>"""
            )
"""TODO:
    Finish implementing template handling.  Will need vimwiki settings 
    info passed for the following:
        vimwiki-option-template_path
        vimwiki-option-template_default
        vimwiki-option-template_ext

"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Convert vimwiki markdown files to html.")
    parser.add_argument("force", type=int, help="Overwrite any previously "
            "existing html file.  0 = no, 1 = yes")
    parser.add_argument("syntax", help="The syntax of the file to be "
            "converted.  The only format  currently supported is markdown. "
            "So this argument should always be markdown.", 
            choices=["markdown"])
    parser.add_argument("extension", help="The extension of the input file. "
            "For example: wiki, txt, or md")
    parser.add_argument("outputdir", help="The absolute path to the directory "
            "where the output html file will be created.")
    parser.add_argument("input_file", type=argparse.FileType('r'), 
            help="The file name (including absolute path) of the markdown "
            "formatted file to be converted to html.")
    parser.add_argument("cssfile", help="The css file (with absolute path) to "
            "be referenced in the resulting html file.")
    ns = parser.parse_args()

    input_file = ns.input_file.read()
    input_filename = os.path.basename(ns.input_file.name)
    # split the filename into the name and the extension and just keep the 
    # first one -- the name.  Then give it a new .html extension
    output_filename = os.path.splitext(input_filename)[0] + '.html' 
    output_file_path = os.path.join(ns.outputdir, output_filename) 

    if ns.force or (os.path.exists(output_file_path) != True):

        class LinkPreprocessor(object):
            """Defined to use as a mixin to get the automatic preprocess and
            postprocess handling.

            """
            def process_percent_codes(self, text, patterns):
                """Look for formatting related percent codes in files.

                Keyword arguments:
                text -- the input markdown file as a string
                patterns -- a dictionary of patterns to search for.  The 
                            following codes are used:
                                %nohtml
                                %title My Title
                                %toc
                                %template

                """
                self.percent_codes = {}
                for key, value in patterns.items():
                    current_pat = re.compile(value, re.MULTILINE)
                    current_match = current_pat.search(text)
                    if current_match:
                        self.percent_codes[key] = current_match.group(1)
                        #cut out the line with the percent code on it.
                        text = (text[:current_match.start()] + 
                                text[current_match.end():])
                    else:
                        self.percent_codes[key] = None
                return text
                
            def preprocess(self, text):
                """Change wikilinks to regular markdown links.

                Keyword arguments:
                text -- the input markdown file as a string

                This method is automatically called when a renderer is 
                rendered.

                The following two wikilink patterns are handled:
                    [[some link text]] 
                    [[link|description]]

                and are change to markdown style links like: 
                    [some link text](some link text.html)

                """
                wiki_desc_link = '\[\[(?P<link>.+)\|(?P<desc>.+)\]\]'
                desc_pat = re.compile(wiki_desc_link)
                text = desc_pat.sub('[\g<desc>](\g<link>.html)', text)
                simple_wiki_link = '\[\[(?P<link>.+)\]\]'
                simple_pat = re.compile(simple_wiki_link)
                text = simple_pat.sub('[\g<link>](\g<link>.html)', text)

                # each of the regular expression patterns has a named group so
                # we can process them all the same way in a function
                # title will be in the form %title This is the Title
                title_text = '^\s*%title\s+(?P<title>.+)\s*'
                template_text = '^\s*%template\s+(?P<template>.+)\s*'
                # %toc
                toc_text = '^\s*(?P<toc>%toc)\s*'
                # %nohtml
                nohtml_text = '^\s*(?P<nohtml>%nohtml)\s*'
                patterns = {'title':title_text, 'toc':toc_text,
                        'no_html':nohtml_text, 'template':template_text}
                text = self.process_percent_codes(text, patterns)
                return text

        class VimwikiTocRenderer(HtmlTocRenderer, LinkPreprocessor):
            pass

        class VimwikiHtmlRenderer(HtmlRenderer, LinkPreprocessor):
            pass

        renderer = VimwikiHtmlRenderer(HTML_TOC)
        to_html = Markdown(renderer, extensions= EXT_NO_INTRA_EMPHASIS | 
            EXT_TABLES | EXT_FENCED_CODE | EXT_AUTOLINK | 
            EXT_STRIKETHROUGH | EXT_SUPERSCRIPT) 
        main_content = to_html.render(input_file)
        if renderer.percent_codes['no_html']:
            print(output_file_path + " not converted due to presence of "
                    "'%nohtml' in the file.")
        else:
            if renderer.percent_codes['toc']:
                toc_renderer = VimwikiTocRenderer()
                to_toc = Markdown(toc_renderer, 
                        extensions = EXT_NO_INTRA_EMPHASIS | EXT_AUTOLINK)
                toc_content = to_toc.render(input_file)
            else:
                toc_content = None

            out = open(output_file_path, 'w')
            out.write(template.render({'toc_content':toc_content,
                'main_content':main_content, 'cssfile':ns.cssfile,
                'title':renderer.percent_codes['title']}))
            out.close()
            print("Converted file to: " + output_file_path)
    else:
        print("The file already exists and the force argument is not 1.")
