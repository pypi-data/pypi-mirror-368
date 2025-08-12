# Outputfile Extension for the Jinja2 Template Engine

[![CI Build Status](https://github.com/jenisys/jinja2-outputfile/actions/workflows/test.yml/badge.svg)](https://github.com/jenisys/jinja2-outputfile/actions/workflows/test.yml)
[![Latest Version](https://img.shields.io/pypi/v/jinja2-outputfile.svg)](https://pypi.python.org/pypi/jinja2-outputfile)
[![License](https://img.shields.io/pypi/l/jinja2-outputfile.svg)](https://github.com/jenisys/jinja2-outputfile/blob/main/LICENSE)

Provides a [Jinja2] directive/extension that supports to redirect
rendered template part(s) to output-file(s).

USE CASES:

* Redirect a rendered [Jinja2] text template part to an output-file
* Use a [Jinja2] template as build script
  if many output-files should be generated from the same data model

FEATURES:

* Output suppression: Output files are only written, if the file contents have changed.
* Verbose mode: Prints which output-files are written and verdict (`CHANGED`, `SAME`).
* Quiet mode: Verbose mode output is suppressed (use: `jinja_outputfile.QuietOutputFileExtension`)

## EXAMPLE 1: Write rendered text to an output-file

```python
# -- FILE: example_one.py
# Redirect rendered text from inside the outputfile block to an output-file.
from jinja2 import Environment
from pathlib import Path

template_as_text = """\
{% outputfile "%s/example_%s.txt"|format(this.output_dir, this.name) -%}
Hello {{this.name}}
{%- endoutputfile %}
"""

# -- EXAMPLE: Using the template
env = Environment(extensions=["jinja2_outputfile.Extension"])
template = env.from_string(template_as_text)
template.render(this=dict(name="Alice", output_dir="."))

# -- POSTCONDITION: FILE WAS CREATED/WRITTEN (with contents)
output_file = Path(".")/"example_Alice.txt"
output_file_contents = output_file.read_text()
assert output_file.exists()
assert output_file_contents == "Hello Alice\n"
```

## EXAMPLE 2: Use multiple output-files

```python
# -- FILE: example.py
from jinja2 import Environment
from pathlib import Path

THIS_TEMPLATE = """
{%- for name in this.names -%}
    {% outputfile "%s/example_%s.txt"|format(this.output_dir, name) -%}
    Hello {{name}}
    {%- endoutputfile %}
{% endfor %}
"""

# -- EXAMPLE: Using the template
env = Environment(extensions=["jinja2_outputfile.Extension"])
code_generator = env.from_string(THIS_TEMPLATE)
code_generator.render(this=dict(names=["Alice", "Bob"], output_dir="."))

# -- POSTCONDITION: FILES were WRITTEN (with contents)
output_file1 = Path(".")/"example_Alice.txt"
output_file2 = Path(".")/"example_Bob.txt"
assert output_file1.exists()
assert output_file2.exists()
assert output_file1.read_text() == "Hello Alice\n"
assert output_file2.read_text() == "Hello Bob\n"

```

[Jinja2]: https://github.com/pallets/jinja/


Rationale
-------------------------------------------------------------------------------

The `outputfile` directive is useful in a code generator use cases
if many output files need to be generated from Jinja2 templates.
In this case, you can provide one template as control script to accomplish this task.


History
-------------------------------------------------------------------------------

* INITIALLY CREATED AS: `simplegen.jinja2_ext.outputfile`
* REFACTORING: Extracted into own standalone package to simplify reuse
  with [Jinja2] template engine.
