Purpose
==========

This is a custom markdown to html processor that integrates with vimwiki to
provide proper creation of html anchor links between wiki pages even when wiki
style links are used instead of markdown links.

It also respects the following Vimwiki percent codes:
- %nohtml
- %toc
- %title
- %template  -- This is parsed but custom template functionality is not 
                provided.

Requirements
=============
Python 3 -- for more robust unicode handling.
[Misaka](http://misaka.61924.nl/) -- a python wrapper for the Sundown markdown
                                     processor.
[Jinja2](http://jinja.pocoo.org/) -- a python templating engine.


Setup
==========
Example installation (note the use of the python 3 specific pip):
    pip-3.2 install misaka Jinja2

git clone this repository

misaka_md2html.py must be executable:
    chmod 755 misaka_md2html.py

Required Vimwiki Settings in vimrc:
1.  custom_wiki2html should point to misaka_md2html.py
2.  path_html must be set
3.  syntax should equal 'markdown'
4.  css_name should point to the css file you want to use.  This has a default value of style.css so copying the provided style.css from autoload/vimwiki/ to your path_html should be sufficient to get started. 


License
==========

[MIT License](http://opensource.org/licenses/mit-license.php)
