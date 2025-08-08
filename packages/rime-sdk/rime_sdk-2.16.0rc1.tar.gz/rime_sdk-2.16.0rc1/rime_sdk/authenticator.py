"""Script for firewall auth before using the SDK."""

import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

_stop = False


class Serv(SimpleHTTPRequestHandler):
    """Local HTTP server for saving auth token."""

    def _set_headers(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message: str) -> bytes:
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET API call."""
        query_components = parse_qs(urlparse(self.path).query)
        if "authToken" in query_components:
            token = query_components["authToken"]
            with open("./token.txt", "w") as file:
                file.write(token[0])
            self._set_headers()
            self.wfile.write(self._html("Authenticated!"))
            global _stop
            _stop = True
        else:
            self.wfile.write(self._html("Not Authenticated!"))
            _stop = True


class StoppableHttpServer(HTTPServer):
    """HTTP server that can be stopped."""

    def serve_forever(self, poll_interval: float = 0.5) -> None:  # noqa: ARG002
        """Handle one request at a time until stopped."""
        while not _stop:
            self.handle_request()


class Authenticator:
    """Firewall authenticator."""

    @staticmethod
    def _prepare_url(host_url: str, email: str, system_account: bool = False) -> str:
        """Prepare the url for auth endpoint."""
        baseurl = host_url + "/v1/auth/authenticate"
        url = (
            baseurl
            + "?"
            + "email="
            + email
            + "&"
            + "system_account="
            + str(system_account)
        )
        return url

    def auth(self, host_url: str, email: str, system_account: bool = False) -> None:
        """Auth method in firewall sdk."""
        url = self._prepare_url(host_url, email, system_account)
        webbrowser.open_new_tab(url)
        httpd = StoppableHttpServer(("localhost", 8099), Serv)
        httpd.serve_forever()
