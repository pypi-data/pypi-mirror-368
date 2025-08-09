from os import path, name as osName
from sys import version_info
from markupsafe import Markup

if version_info.major == 2:
    FileNotFoundError = IOError

class fontpicker(object):
    def __init__(self, app=None, jqueryUI=True,  local=[]):
        """
        Initiating the extension and seting up important variables
        @param: app flask application instance (default None).
        @param: jqueryUI to include or exclude jquery-ui source code in loader()
        @param: local contains jquery-UI webfont local sourcecode files (default [])
        """
        self.app = app
        self.local = local
        self.jqueryUI = jqueryUI
        if self.app is not None:
            self.init_app(app)
        else:
            # throwing error for not receiving app
            raise(AttributeError("must pass app to datepicker(app=)"))
        if self.local != []:
            # checking the length of the received list and throwing error
            numberOfFiles = 5 if jqueryUI else 3
            if len(self.local) != numberOfFiles:
                raise(
                    TypeError(
                        "datepicker(local=) requires a list of i" +
                        numberOfFiles + " files (if jqueryUI enabled jquery-ui.js," +
                        "jquery-ui.css) webfont.js, webfont-select.js and webfont-select.css"))
        self.injectThem()  # responsible of injecting modals into the template

    def init_app(self, app):
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        pass

    def injectThem(self):
        """ datepicker injecting itself into the template as datepicker """
        @self.app.context_processor
        def inject_vars():
            return dict(fontpicker=self)

    def loader(self):
        """
        Function that allows to separate loading the plugin and its dependencies and initiating the JS plugin
        """
        self.html = ""  # html tags will end-up here
        if self.local == []:
            links = [
                'https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css',
                'https://code.jquery.com/ui/1.12.1/jquery-ui.min.js',
                'https://ajax.googleapis.com/ajax/libs/webfont/1/webfont.js',
                'https://www.jqueryscript.net/demo/Google-Web-Font-Picker-Plugin-With-jQuery-And-jQuery-UI-Webfont-selector/webfont.select.js',
                'https://www.jqueryscript.net/demo/Google-Web-Font-Picker-Plugin-With-jQuery-And-jQuery-UI-Webfont-selector/webfont.select.css'
            ]
        else:
            links = self.local

            def togglePath(rev=False, links=links):
                """
                    Function to fix windows OS relative path issue
                    ISSUE 1 : windows os path
                    if windows used and windows path not used.
                """
                if osName == 'nt':
                    order = ['\\', '/'] if rev else ['/', '\\']
                    for linkIndex, link in enumerate(links):
                        links[linkIndex] = link.replace(order[0], order[1])

            togglePath(False)
            # checking if Jquery UI files exist
            for link in links:
                if not path.isfile(link):
                    raise(FileNotFoundError(
                        "datepicker.loader() file not found " + link))
            togglePath(True)
    
        def toDo (self):
            if self.local == []:
                self.html += '<script src="%s"></script>\n' % link if link.endswith('.js') else '<link href="%s" rel="stylesheet">\n' % link
            else:
                self.html += '<script src="/%s"></script>\n' % link if link.endswith('.js') else '<link href="/%s" rel="stylesheet">\n' % link
    
        for link in links:
            if self.jqueryUI:
                toDo(self)
            else:
                try:
                    link.index('jquery-ui')
                except Exception:
                    toDo(self)
        return Markup(self.html)  # making sure html safe

    def picker(self, ids=["#fontpicker"],
               families='["Droid Sans", "Roboto", "Roboto Condensed", "Signika"]',
               loadAll='true',
               defaultFont='',
               urlCss='',
               spaceChar='+'):
        """
        fontpicker initializer, it produces a javascript code to load the plugin
        with passed arguments
        @param: ids list of identifiers which jquery will assign fontpickers to
        (default ['#fontpicker']).
        @param: families list of the font families to be displayed
        (default: ["Droid Sans", "Roboto", "Roboto Condensed", "Signika"])
        @param: loadAll to load all the selected fonts
        (default 'true').
        @param: defaultFont default font to load at first
        (default: 'Roboto').
        @param: urlCss to load fonts with local css file
        (default: '').
        @param: spaceChar spacing character used in local css file
        (default: '+').
        """
        toReturn = ""
        for id in ids:
            toReturn += " ".join(['<script>',
            '$(document).ready(function() {'
            '$("%s").wfselect({' % id,
            'fonts: { google: { families: %s,' % families,
            'url_generation: {base_url: "%s", space_char: "%s"}}},' % (urlCss, spaceChar),
            'load_all_fonts: %s,' % loadAll,
            'default_font_name: {type: "google", name: String($("%s").val())}' % id,
            '}).on("wfselectchange", function (event, fontInfo){',
            '$("%s").val(fontInfo["font-family"])}) })' % id,
            '</script>', "\n"])
        return Markup(toReturn)
