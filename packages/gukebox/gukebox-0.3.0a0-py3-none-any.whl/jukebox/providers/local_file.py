import logging
import time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread

level = logging.INFO
LOGGER = logging.getLogger("jukebox-providers")
LOGGER.setLevel(level)
console_handler = logging.StreamHandler()
console_handler.setLevel(level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s\t - %(message)s")
console_handler.setFormatter(formatter)
LOGGER.addHandler(console_handler)

MUSIC_DIRECTORY = "/Users/theophile/Developer/Théophile/jukebox/library/UnknownAlbum"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=MUSIC_DIRECTORY, **kwargs)


class HttpServer(Thread):
    """A simple HTTP Server in its own thread"""

    def __init__(self, port):
        super().__init__()
        self.daemon = True
        handler = Handler
        self.httpd = TCPServer(("", port), handler)

    def run(self):
        """Start the server"""
        LOGGER.info("Start HTTP server")
        self.httpd.serve_forever()

    def stop(self):
        """Stop the server"""
        LOGGER.info("Stop HTTP server")
        self.httpd.socket.close()


def main():
    server = HttpServer(8080)
    server.start()
    try:
        time.sleep(10**8)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
