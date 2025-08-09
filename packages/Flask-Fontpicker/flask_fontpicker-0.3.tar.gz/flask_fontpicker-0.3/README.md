<h1 align='center'> flask_fontpicker </h1>
<h3 align='center'>A Flask extension for Jquery-ui google font picker, it makes adding and customizing multiple font pickers simpler and less time consuming.</h3>

## Install:
#### - With pip
> - `pip install Flask-Fontpicker` <br />

#### - From the source:
> - `git clone https://github.com/mrf345/flask_fontpicker.git`<br />
> - `cd flask_fontpicker` <br />
> - `python setup.py install`

## Setup:
#### - Inside Flask app:
```python
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_fontpicker import fontpicker

app = Flask(__name__)
Bootstrap(app)
fontpicker(app)
```

#### - Inside jinja template:
```jinja
{% extends 'bootstrap/base.html' %}
{% block scripts %}
  {{ super() }}
  {{ fontpicker.loader() }} {# to load jQuery-ui #}
  {{ fontpicker.picker(ids=["#dp"]) }}
{% endblock %}
{% block content %}
  <form class="verticalform">
    <input type="text" id="dp" class="form-control" />
  </form>
{% endblock %}
```

## Settings:
#### - Options:
> The accepted arguments to be passed to the `fontpicker.picker()` function are as follow:
```python
def picker(self, ids=["#fontpicker"], # list of identifiers will be passed to Jquery to select element
                  families='["Droid Sans", "Roboto", "Roboto Condensed", "Signika"]',
                  # list of the font families to be displayed
                  loadAll='true', # to load all the selected fonts
                  default='Roboto', # default font to load at first
                  urlCss='', # to load fonts with local css file
                  spaceChar='+'): # spacing character used in local css file
```

#### - Local source:
> by default the extension will load Jquery-ui plugin from [a remote CDN][25530337]. Although you can configure that to be locally through passing a list of .js and .css files into the fontpicker module like such:
```python
fontpicker(app=app, local=[
  'static/js/jquery-ui.js', 
  'static/css/jquery-ui.css', 
  'static/js/webfont.js',
  'static/css/webfont.select.css',
  'static/js/webfont.select.js'
  ])
```
_The order in-which the items of list are passed is not of importance, it will be auto detected via file extension_

[25530337]: https://code.jquery.com/ui/ "Jquery-ui CDN"

## Credit:
> - [Fontpicker][1311353e]: jQuery-ui web google font picker extension.

  [1311353e]: https://www.jqueryscript.net/text/Google-Web-Font-Picker-Plugin-With-jQuery-And-jQuery-UI-Webfont-selector.html "jQuery-UI scripts page"
