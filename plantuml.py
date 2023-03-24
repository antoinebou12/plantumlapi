from os import makedirs, path
from io import open
from typing import Optional
from zlib import compress
import httpx

import typer

app = typer.Typer()

# Example usage
diagram = """
@startuml
title Example Diagram
actor User
User -> "Website" : Requests Page
"Website" -> "Database" : Retrieves Data
"Database" --> "Website" : Returns Data
"Website" -> User : Sends Page
@enduml
"""

class PlantUMLError(Exception):
    """
    Error in processing.
    """
    pass


class PlantUMLConnectionError(PlantUMLError):
    """
    Error connecting or talking to PlantUML Server.
    """
    pass


class PlantUMLHTTPError(PlantUMLConnectionError):
    """
    Request to PlantUML server returned HTTP Error.
    """

    def __init__(self, response, content, *args, **kwdargs):
        self.response = response
        self.content = content
        message = "%d: %s" % (self.response.status_code, self.response.reason_phrase)
        if not getattr(self, 'message', None):
            self.message = message
        super().__init__(message, *args, **kwdargs)

class PlantUML:
    """Connection to a PlantUML server with optional authentication.

    All parameters are optional.

    :param str url: URL to the PlantUML server image CGI. defaults to
                    http://www.plantuml.com/plantuml/img/
    :param dict basic_auth: This is if the plantuml server requires basic HTTP
                    authentication. Dictionary containing two keys, 'username'
                    and 'password', set to appropriate values for basic HTTP
                    authentication.
    :param dict form_auth: This is for plantuml server requires a cookie based
                    webform login authentication. Dictionary containing two
                    primary keys, 'url' and 'body'. The 'url' should point to
                    the login URL for the server, and the 'body' should be a
                    dictionary set to the form elements required for login.
                    The key 'method' will default to 'POST'. The key 'headers'
                    defaults to
                    {'Content-type':'application/x-www-form-urlencoded'}.
                    Example: form_auth={'url': 'http://example.com/login/',
                    'body': { 'username': 'me', 'password': 'secret'}
    :param dict http_opts: Extra options to be passed off to the
                    httplib2.Http() constructor.
    :param dict request_opts: Extra options to be passed off to the
                    httplib2.Http().request() call.

    """
    def __init__(self, url: str, basic_auth: Optional[dict] = None, form_auth: Optional[dict] = None,
                    http_opts: Optional[dict] = None, request_opts: Optional[dict] = None):
        if basic_auth is None:
            basic_auth = {}
        if form_auth is None:
            form_auth = {}
        if http_opts is None:
            http_opts = {}
        if request_opts is None:
            request_opts = {}

        self.url = url
        self.request_opts = request_opts
        self.auth_type = 'basic_auth' if basic_auth else ('form_auth' if form_auth else None)
        self.auth = basic_auth or form_auth or None

        self.client = httpx.Client(**http_opts, proxies=http_opts.get('proxies', None))

        if self.auth_type == 'basic_auth':
            self.client.auth = (self.auth['username'], self.auth['password'])
        elif self.auth_type == 'form_auth':
            if 'url' not in self.auth:
                raise PlantUMLError(
                    "The form_auth option 'url' must be provided and point to "
                    "the login url.")
            if 'body' not in self.auth:
                raise PlantUMLError(
                    "The form_auth option 'body' must be provided and include "
                    "a dictionary with the form elements required to log in. "
                    "Example: form_auth={'url': 'http://example.com/login/', "
                    "'body': { 'username': 'me', 'password': 'secret'}")
            login_url = self.auth['url']
            body = self.auth['body']
            method = self.auth.get('method', 'POST')
            headers = self.auth.get(
                'headers', {'Content-type': 'application/x-www-form-urlencoded'})
            try:
                response = self.client.request(method, login_url, headers=headers, data=body)
            except httpx.HTTPError as e:
                raise PlantUMLConnectionError(e) from e
            if response.status_code != 200:
                raise PlantUMLHTTPError(response, "Login failed. Check your form_auth settings.")
            self.request_opts['Cookie'] = response.cookies.get_dict()

    def get_url(self, plantuml_text):
        """Return the server URL for the image.
        You can use this URL in an IMG HTML tag.

        :param str plantuml_text: The plantuml markup to render
        :returns: the plantuml server image URL
        """
        return self.url + self.deflate_and_encode(plantuml_text)

    def processes(self, plantuml_text):
        """Processes the plantuml text into the raw PNG image data.
        :param str plantuml_text: The plantuml markup to render
        :returns: the raw image data
        """
        url = self.get_url(plantuml_text)
        try:
            response = httpx.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise PlantUMLHTTPError(e, "") from e
        return response.content

    def processes_file(self, filename, outfile=None, errorfile=None, directory=''):
        """Take a filename of a file containing plantuml text and processes
        it into a .png image.

        :param str filename: Text file containing plantuml markup
        :param str outfile: Filename to write the output image to. If not
                    supplied, then it will be the input filename with the
                    file extension replaced with '.png'.
        :param str errorfile: Filename to write server html error page
                    to. If this is not supplined, then it will be the
                    input ``filename`` with the extension replaced with
                    '_error.html'.
        :returns: ``True`` if the image write succedded, ``False`` if there was
                    an error written to ``errorfile``.
        """
        if outfile is None:
            outfile = f'{path.splitext(filename)[0]}.png'
        if errorfile is None:
            errorfile = f'{path.splitext(filename)[0]}_error.html'
        if directory and not path.exists(directory):
            makedirs(directory)
        data = open(filename).read()
        try:
            content = self.processes(data)
        except PlantUMLHTTPError as e:
            with open(path.join(directory, errorfile), 'w') as err:
                err.write(e.content)
            return False
        with open(path.join(directory, outfile), 'wb') as out:
            out.write(content)
        return True


    def deflate_and_encode(self, plantuml_text):
        """zlib compress the plantuml text and encode it for the plantuml server.
        """
        zlibbed_str = compress(plantuml_text.encode('utf-8'))
        compressed_string = zlibbed_str[2:-4]
        return self.encode(compressed_string)


    def encode(self, data):
        """encode the plantuml data which may be compresses in the proper
        encoding for the plantuml server
        """
        res = ""
        for i in range(0, len(self), 3):
            if i + 2 == len(self):
                res += self._encode3bytes(self[i], self[i + 1], 0)
            elif i + 1 == len(self):
                res += self._encode3bytes(self[i], 0, 0)
            else:
                res += self._encode3bytes(self[i], self[i + 1], self[i + 2])
        return res


    def _encode3bytes(self, b1, b2, b3):
        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F
        res = ""
        res += self._encode6bit(c1 & 0x3F)
        res += self._encode6bit(c2 & 0x3F)
        res += self._encode6bit(c3 & 0x3F)
        res += self._encode6bit(c4 & 0x3F)
        return res


    def _encode6bit(self, b):
        if b < 10:
            return chr(48 + b)
        b -= 10
        if b < 26:
            return chr(65 + b)
        b -= 26
        if b < 26:
            return chr(97 + b)
        b -= 26
        if b == 0:
            return '-'
        return '_' if b == 1 else '?'

    @app.command(
        help='Generate images from plantuml defined files using plantuml server'
    )
    def generate_images(files: list[str], out: str = '', server: str = 'http://www.plantuml.com/plantuml/img/'):
        """Generate images from plantuml defined files using plantuml server"""
        pl = PlantUML(
            url=server,
            http_opts={'timeout': 60},
            request_opts={'User-Agent': 'plantuml-markdown/0.1.0'}
        )
        results = []
        for filename in files:
            gen_success = pl.processes_file(filename, directory=out)
            results.append({'filename': filename, 'gen_success': gen_success})

        typer.echo(results)


    @app.command(
        help='Generate images from plantuml defined files using plantuml server'
    )
    def generate_image(
        file: str,
        out: str = '',
        server: str = 'http://www.plantuml.com/plantuml/img/',
        auth: dict = None
    ):
        """Generate images from plantuml defined files using plantuml server"""
        pl = PlantUML(
            url=server,
            http_opts={'timeout': 60},
            request_opts={'User-Agent': 'plantuml-markdown/0.1.0'},
            auth=auth
        )
        gen_success = pl.processes_file(file, directory=out)
        typer.echo(gen_success
    )

def main():
    app()


if __name__ == '__main__':
    main()
