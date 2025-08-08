# WebWidgets

![CI Status](https://img.shields.io/github/actions/workflow/status/mlaasri/WebWidgets/ci-full.yml?branch=main)

A Python package for creating web UIs

## Installation

You can install **WebWidgets** with `pip`. To install the latest stable version, run:

```bash
pip install webwidgets
```

## Usage

**WebWidgets** allows you to create custom widgets and build websites with them. For example:

```python
import webwidgets as ww
from webwidgets.compilation.html import HTMLNode, RawText

# A <div> element
class Div(HTMLNode):
    pass

# A simple text widget
class Text(ww.Widget):
    def build(self):
        return Div([RawText("Hello, World!")])

# A website with one page containing a Text widget
page = ww.Page([Text()])
website = ww.Website([page])

# Compile the website into HTML code
compiled = website.compile()
print(compiled.html_content[0])
```

Prints the following result:

```console
<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <div>
            Hello, World!
        </div>
    </body>
</html>
```