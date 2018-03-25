"""
Support for using the CodeMirror code editor as a wiki content editor.
"""

import django
from django import forms
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from wiki.editors.base import BaseEditor
from wiki.editors.markitup import MarkItUpAdminWidget


class CodeMirrorWidget(forms.Widget):
    """
    Use CodeMirror as a Django form widget (like a textarea).
    """
    def __init__(self, attrs=None):
        # The 'rows' and 'cols' attributes are required for HTML correctness.
        default_attrs = {
            'class': 'markItUp',
            'rows': '10',
            'cols': '40',
            'aria-describedby': 'hint_id_content'
        }
        if attrs:
            default_attrs.update(attrs)
        super(CodeMirrorWidget, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        # TODO: Remove Django 1.11 upgrade shim
        # SHIM: Compensate for build_attrs() implementation change in 1.11
        if django.VERSION < (1, 11):
            final_attrs = self.build_attrs(attrs, name=name)
        else:
            extra_attrs = attrs.copy()
            extra_attrs['name'] = name
            final_attrs = self.build_attrs(self.attrs, extra_attrs=extra_attrs)  # pylint: disable=redundant-keyword-arg

        # TODO use the help_text field of edit form instead of rendering a template

        return render_to_string('wiki/includes/editor_widget.html',
                                {'attrs': mark_safe(flatatt(final_attrs)),
                                 'content': conditional_escape(force_unicode(value)),
                                 })


class CodeMirror(BaseEditor):
    """
    Wiki content editor using CodeMirror.
    """
    editor_id = 'codemirror'

    def get_admin_widget(self, instance=None):
        return MarkItUpAdminWidget()

    def get_widget(self, instance=None):
        return CodeMirrorWidget()

    class AdminMedia(object):  # pylint: disable=missing-docstring
        css = {
            'all': ("wiki/markitup/skins/simple/style.css",
                    "wiki/markitup/sets/admin/style.css",)
        }
        js = ("wiki/markitup/admin.init.js",
              "wiki/markitup/jquery.markitup.js",
              "wiki/markitup/sets/admin/set.js",
              )

    class Media(object):  # pylint: disable=missing-docstring
        css = {
            'all': ("js/vendor/CodeMirror/codemirror.css",)
        }
        js = ("js/vendor/CodeMirror/codemirror.js",
              "js/vendor/CodeMirror/addons/xml.js",
              "js/vendor/CodeMirror/addons/edx_markdown.js",
              "js/wiki/accessible.js",
              "js/wiki/CodeMirror.init.js",
              )
