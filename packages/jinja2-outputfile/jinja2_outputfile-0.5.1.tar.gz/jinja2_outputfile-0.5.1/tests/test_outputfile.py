from __future__ import absolute_import, print_function
from jinja2 import Environment
from jinja2_outputfile import Path


# -----------------------------------------------------------------------------
# TEST SUPPORT FUNCTIONS
# -----------------------------------------------------------------------------
DEFAULT_EXTENSION = "jinja2_outputfile.OutputFileExtension"

def render_template(template_text, extension=None, **data):
    # -- WHEN: I render the template
    this_extension = extension or DEFAULT_EXTENSION
    env = Environment(extensions=[this_extension])
    template = env.from_string(template_text)
    text = template.render(**data)
    return text


def textfile_contents(filename, encoding=None):
    encoding = encoding or "utf-8"
    contents = Path(filename).read_text(encoding=encoding)
    return contents
    # -- ALTERNATIVE:
    # with open(str(filename), encoding="UTF-8") as f:
    #     contents = f.read()
    # return contents


def assert_textfile_has_contents(filename, expected_contents):
    assert filename.exists()
    assert filename.is_file()
    actual_contents = textfile_contents(filename).rstrip()
    assert actual_contents == expected_contents


def assert_directory_has_files(directory, expected_files):
    actual_files = [str(p.name) for p in sorted(directory.iterdir()) if p.is_file()]
    assert actual_files == expected_files


# -----------------------------------------------------------------------------
# TEMPLATES
# -----------------------------------------------------------------------------
TEMPLATE4ONE_FILE = u"""
{% outputfile "%s/example_%s.txt"|format(this.output_dir, this.name) -%}
Hello {{this.name}}
{%- endoutputfile %}
"""

TEMPLATE4MANY_FILES = u"""
{%- for name in this.names -%}
    {% outputfile "%s/example_%s.txt"|format(this.output_dir, name) -%}
    Hello {{name}}
    {%- endoutputfile %}
{%- endfor %}
"""


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
#    {% outputfile "{output_dir}/example_{name}.txt".format(output_dir=output_dir, name=name) -%}
class TestOutputFileExtension(object):
    def test_outputfile_with_one_file(self, tmp_path):
        # -- WHEN: I render the template
        output_dir = tmp_path
        data = dict(name=u"Alice", output_dir=output_dir)
        text = render_template(TEMPLATE4ONE_FILE, this=data)
        print(text)

        # -- THEN: the output-file exists and has the contents
        expected = u"Hello Alice"
        assert_textfile_has_contents(output_dir/"example_Alice.txt", expected)


    def test_outputfile_with_many_files(self, tmp_path):
        # -- WHEN: I render the template
        output_dir = tmp_path
        data = dict(names=[u"Alice", u"Bob"], output_dir=output_dir)
        text = render_template(TEMPLATE4MANY_FILES, this=data)
        print(text)

        # -- THEN: the following files exist with contents
        expected1 = u"Hello Alice"
        expected2 = u"Hello Bob"
        assert_directory_has_files(output_dir, ["example_Alice.txt", "example_Bob.txt"])
        assert_textfile_has_contents(output_dir/"example_Alice.txt", expected1)
        assert_textfile_has_contents(output_dir/"example_Bob.txt", expected2)


    def test_outputfile_creates_nonexisting_directory(self, tmp_path):
        the_template = """
{% outputfile "%s/subdir/example_%s.txt"|format(this.output_dir, this.name) -%}
Hello {{this.name}}
{%- endoutputfile %}
"""

        # -- GIVEN: the output-sub-directory does not exist
        output_dir = tmp_path
        output_subdir = output_dir/"subdir"
        assert not output_subdir.exists()
        assert not output_subdir.is_dir()

        # -- WHEN: I render the template
        data = dict(name="Charly", output_dir=output_dir)
        text = render_template(the_template, this=data)
        print(text)

        # -- THEN: the output-file should contain:
        expected = "Hello Charly"
        assert_textfile_has_contents(output_dir/"subdir/example_Charly.txt", expected)
        assert output_subdir.exists()
        assert output_subdir.is_dir()


class TestVerboseMode:
    EXTENSION = "jinja2_outputfile.OutputFileExtension"

    def test_output_if_file_not_exists(self, tmp_path, capsys):
        # -- GIVEN: the output-file does not exist
        output_dir = tmp_path
        output_file = output_dir/"example_Alice.txt"
        assert not output_file.exists()

        # -- WHEN: I render the template
        data = dict(name="Alice", output_dir=output_dir)
        render_template(TEMPLATE4ONE_FILE, this=data, extension=self.EXTENSION)

        # -- THEN: the captured-output contains ... and the output-file exists
        output_dir = output_dir.as_posix()  # -- NORMALIZE-PATH
        expected = "OUTPUTFILE: {output_dir}/example_Alice.txt ...".format(output_dir=output_dir)
        captured = capsys.readouterr()
        captured_output = captured.out.strip()
        print("CAPTURED:\n{}".format(captured.out))
        assert captured_output == expected
        assert "(overwritten)" not in captured.out
        assert output_file.exists()

    def test_output_if_file_exists_with_other_contents(self, tmp_path, capsys):
        # -- GIVEN: the output-file exists with OTHER contents
        output_dir = tmp_path
        output_file = output_dir/"example_Bob.txt"
        output_file.write_text(u"Hello OTHER", encoding="UTF-8")
        assert output_file.exists()

        # -- WHEN: I render the template
        data = dict(name="Bob", output_dir=output_dir)
        render_template(TEMPLATE4ONE_FILE, this=data, extension=self.EXTENSION)

        # -- THEN: the output contains ... and the output-file exists
        output_dir = output_dir.as_posix()  # -- NORMALIZE-PATH
        expected = "OUTPUTFILE: {output_dir}/example_Bob.txt ... (CHANGED)".format(output_dir=output_dir)
        captured = capsys.readouterr()
        captured_output = captured.out.strip()
        print("CAPTURED:\n{}".format(captured.out))
        assert captured_output == expected
        assert output_file.exists()

    def test_output_if_file_exists_with_same_contents(self, tmp_path, capsys):
        # -- GIVEN: the output-file exists with OTHER contents
        output_dir = tmp_path
        output_file = output_dir/"example_Charly.txt"
        output_file.write_text(u"Hello Charly\n", encoding="UTF-8")
        assert output_file.exists()

        # -- WHEN: I render the template twice
        data = dict(name="Charly", output_dir=output_dir)
        render_template(TEMPLATE4ONE_FILE, this=data, extension=self.EXTENSION)

        # -- THEN: the output contains ... and the output-file exists
        output_dir = output_dir.as_posix()  # -- NORMALIZE-PATH
        expected = "OUTPUTFILE: {output_dir}/example_Charly.txt ... (SAME)".format(output_dir=output_dir)
        captured = capsys.readouterr()
        captured_output = captured.out.strip()
        print("CAPTURED:\n{}".format(captured.out))
        assert captured_output == expected
        assert output_file.exists()

    def test_output_if_render_same_template_twice(self, tmp_path, capsys):
        # -- GIVEN: the output-file exists with OTHER contents
        output_dir = tmp_path
        output_file = output_dir/"example_Doro.txt"
        assert not output_file.exists()

        # -- WHEN: I render the template twice
        data = dict(name="Doro", output_dir=output_dir)
        render_template(TEMPLATE4ONE_FILE, this=data, extension=self.EXTENSION)
        render_template(TEMPLATE4ONE_FILE, this=data, extension=self.EXTENSION)

        # -- THEN: the output contains ... and the output-file exists
        output_dir = output_dir.as_posix()  # -- NORMALIZE-PATH
        expected = """
OUTPUTFILE: {output_dir}/example_Doro.txt ...
OUTPUTFILE: {output_dir}/example_Doro.txt ... (SAME)
""".format(output_dir=output_dir).strip()
        captured = capsys.readouterr()
        captured_output = captured.out.strip()
        print("CAPTURED:\n{}".format(captured.out))
        assert captured_output == expected


class TestQuietMode:
    EXTENSION = "jinja2_outputfile.QuietOutputFileExtension"

    @classmethod
    def assert_without_output_for_render_template(cls, template_text, capsys, **data):
        # -- WHEN: I render the template
        render_template(template_text, this=data, extension=cls.EXTENSION)

        # -- THEN: the captured-output contains ... and the output-file exists
        captured = capsys.readouterr()
        captured_output = captured.out.strip()
        print("CAPTURED:\n{}".format(captured.out))
        assert not captured_output

    def test_without_output_if_file_not_exists(self, tmp_path, capsys):
        # -- GIVEN: the output-file does not exist
        output_dir = tmp_path
        output_file = output_dir/"example_Alice.txt"
        assert not output_file.exists()

        # -- WHEN: I render the template
        data = dict(name="Alice", output_dir=output_dir)
        self.assert_without_output_for_render_template(TEMPLATE4ONE_FILE, capsys, **data)

    def test_without_output_if_file_exists_with_other_contents(self, tmp_path, capsys):
        # -- GIVEN: the output-file exists with OTHER contents
        output_dir = tmp_path
        output_file = output_dir/"example_Bob.txt"
        output_file.write_text(u"Hello OTHER", encoding="UTF-8")
        assert output_file.exists()

        # -- WHEN: I render the template
        data = dict(name="Bob", output_dir=output_dir)
        self.assert_without_output_for_render_template(TEMPLATE4ONE_FILE, capsys, **data)


    def test_without_output_if_file_exists_with_same_contents(self, tmp_path, capsys):
        # -- GIVEN: the output-file exists with OTHER contents
        output_dir = tmp_path
        output_file = output_dir/"example_Charly.txt"
        output_file.write_text(u"Hello Charly\n", encoding="UTF-8")
        assert output_file.exists()

        # -- WHEN: I render the template twice
        data = dict(name="Charly", output_dir=output_dir)
        self.assert_without_output_for_render_template(TEMPLATE4ONE_FILE, capsys, **data)


class TestExtension:
    """Ensure official documented Extension class works as expected."""
    EXTENSION = "jinja2_outputfile.Extension"

    def test_usage(self, tmp_path):
        # -- WHEN: I render the template
        output_dir = tmp_path
        data = dict(name=u"Annabelle", output_dir=output_dir)
        render_template(TEMPLATE4ONE_FILE, this=data)

        # -- THEN: the output-file exists and has the contents
        expected = u"Hello Annabelle"
        assert_textfile_has_contents(output_dir/"example_Annabelle.txt", expected)

