"""
local_storage_server.py
Provides a simple HTTP server to serve locally stored files.
"""

import http.server
import socketserver
import os

class LocalStorageServer:
    """
    A simple HTTP server that serves files from a local directory.
    """

    def __init__(self, port: int, storage_directory: str):
        """
        Initializes the local storage server.

        Args:
            port (int): The port on which the server will run.
            storage_directory (str): The directory to serve files from.
        """
        self.port = port
        self.storage_directory = storage_directory
        self.httpd = None

    def start_server(self):
        """
        Starts a blocking HTTP server on self.port, serving self.storage_directory.
        """
        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
            *args, directory=self.storage_directory, **kwargs
        )
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        print(f"[LocalStorageServer] Serving '{self.storage_directory}' at port {self.port}")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            self.stop_server()

    def stop_server(self):
        """
        Stops the running HTTP server.
        """
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print("[LocalStorageServer] Server stopped.")
