# -*- coding: utf-8 -*-
"""
This module provides a Jinja2 directive to capture the output within its block
and write it to an output file.

.. code-block:: jinja2

    {% outputfile "xxx.out" %}
    ...lorem ipsum...
    {% endoutputfile %}


.. note:: Rationale

    It is sometimes much easier to generate all data that is normally split-up
    into multiple files into one template file  that contains the logic
    how these parts are split-up. Otherwise, you would need to provide a
    multi-stage code generator.
"""

from __future__ import absolute_import, print_function
# XXX from codecs import open  # -- HINT: py2/py3 compatible
import os
from jinja2 import nodes
from jinja2.ext import Extension as _Extension
from ._pathlib import Path


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
DEFAULT_ENCODING = "UTF-8"
DEFAULT_ERRORS = None


# -----------------------------------------------------------------------------
# SUPPORT FUNCTIONALITY:
# -----------------------------------------------------------------------------
class Reporter(object):
    ANNOTATION_CREATED = ""
    ANNOTATION_CHANGED = " (CHANGED)"
    ANNOTATION_SAME = " (SAME)"
    ENCODING = DEFAULT_ENCODING
    ERRORS = DEFAULT_ERRORS
    OUTPUT_SCHEMA = "OUTPUTFILE: {filename} ...{annotation}"
    SHOW_SAME = True

    @classmethod
    def report_outfile(cls, filename, contents, encoding=None, errors=None):
        encoding = encoding or cls.ENCODING
        errors = errors or cls.ERRORS
        annotation = cls.ANNOTATION_CREATED
        if filename.exists():
            annotation = cls.ANNOTATION_CHANGED
            this_contents = filename.read_text(encoding=encoding, errors=errors)
            if contents == this_contents:
                # -- CASE SAME: Show or not show output-file.
                annotation = cls.ANNOTATION_SAME
                if not cls.SHOW_SAME:
                    return

        # -- DISPLAY OUTPUT-FILE (and its state)
        filename = Path(filename).as_posix()  # SIMPLIFY: Testing on Windows.
        print(cls.OUTPUT_SCHEMA.format(filename=filename, annotation=annotation))


class NullReporter(object):
    """Implements the NULL design pattern: NO OUTPUT"""
    @classmethod
    def report_outfile(cls, filename, contents, encoding=None):
        pass



# -----------------------------------------------------------------------------
# JINJA2 TEMPLATE EXTENSIONS:
# -----------------------------------------------------------------------------
class OutputFile(_Extension):
    """
    Jinja2 extension that redirects the output in its block to a file.

    .. code-block:: jinja2

        {% outputfile "<filename>" -%}
        ...lorem ipsum...
        {%- endoutputfile %}
    """
    tags = set(["outputfile"])
    ENCODING = "UTF-8"
    ERRORS = None
    REPORTER_CLASS = Reporter

    def parse(self, parser):
        """Used by the Jinja2 parser to delegate parsing of the directive/tag.

        :param parser:  Parser to use.
        :return: Jinja2 node(s) for the parser.
        """
        lineno = next(parser.stream).lineno
        filename = parser.parse_expression()
        encoding = nodes.Const(self.ENCODING)
        # MAYBE: parser.stream.expect('name:encoding')
        # MAYBE: name = parser.stream.expect('name')
        body = parser.parse_statements(["name:endoutputfile"], drop_needle=True)

        # -- RETURN: nodes.CallBlock/Call that is executed later-on.
        return nodes.CallBlock(
            self.call_method("_output_to_file", [filename, encoding]),
            [], [], body).set_lineno(lineno)

    def _use_reporter(self):
        reporter = getattr(self, "_reporter", None)
        if reporter is None:
            # -- NOTE: Allocate only once.
            self._reporter = self.REPORTER_CLASS()
            reporter = self._reporter
        return reporter

    def _output_to_file(self, filename, encoding, caller):
        """
        Stores the output of the template-block in an output file.

        Extension/Tag core functionality, called by the CodeGenerator
        (when the parsed nodes are processed).

        :param filename:  File name of the output file.
        :param encoding:  File encoding to use (UTF-8, ...)
        :param caller:    Macro that encapsulates the template block contents.
        :return: Empty string (because block-contents are redirected to file).
        """
        captured_text = caller()
        if not captured_text.endswith("\n"):
            captured_text += "\n"

        this_filename = Path(filename)
        basedir = this_filename.parent or "."
        if not basedir.is_dir():
            os.makedirs(str(basedir))

        self._use_reporter().report_outfile(this_filename, captured_text)
        this_filename.write_text(captured_text, encoding=encoding, errors=self.ERRORS)
        return ""


class QuietOutputFile(OutputFile):
    """
    Provides :class:OutputFileExtension directive in quiet mode.
    """
    REPORTER_CLASS = NullReporter


# -- BACKWARD-COMPATIBLE CLASS ALIASES:
OutputFileExtension = OutputFile
QuietOutputFileExtension = QuietOutputFile


class Extension(_Extension):
    """
    Provides the combined jinja2 extension(s) of this package:

    * ``outputfile`` (as extension)

    This simplifies usage, like:

    .. code-block:: python

        # -- FILE: use_this_jinja_extension.py
        from jinja2 import Environment

        env = Environment(extensions=["jinja2_outputfile.Extension"]
        template = env.get_template("some_template.jinja")
        template.render(files=...)
    """
    def __init__(self, environment):
        super(Extension, self).__init__(environment)
        environment.add_extension(OutputFile)
