#!/usr/bin/env python3

"""
A basic Python 3 HTTP/1.1 server.
"""

import socketserver
import pathlib
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8000
BUFSIZE = 4096
LINE_ENDING='\r\n'
SERVE_PATH = pathlib.Path('www').resolve()
HTTP_1_1 = 'HTTP/1.1'

class LabHttpTcpServer(socketserver.TCPServer):
    allow_reuse_address = True

class LabHttpTCPHandler(socketserver.StreamRequestHandler):
    def __init__(self, *args, **kwargs):
        self.charset = "UTF-8"
        self.serve_path = pathlib.Path("www").resolve()
        super().__init__(*args, **kwargs)

    def receive_line(self):
        return self.rfile.readline().strip().decode(self.charset, 'ignore')
    
    def send_line(self, line):
        self.wfile.write((line + LINE_ENDING).encode(self.charset, 'ignore'))

    def handle(self):
        # Receive and decode the request
        request_line = self.rfile.readline().strip().decode('utf-8')
        
        # Extract the method and path from the request
        method, path, _ = request_line.split(' ', 2)
        if method != "GET":
            self.send_error(405, "Method Not Allowed")
            return
        decoded_path = self.percent_decode(path)
        headers = self.parse_headers()
        
        serving_dir = Path("./www")
        full_path = serving_dir / decoded_path.lstrip("/")  # this doesn't work unless I remove the first "/"
        if not full_path.exists():
            self.send_error(404, "Not Found")
        if full_path.is_dir():
            if decoded_path[-1] != "/":
                # redirect to directory path
                self.send_error(301, "Moved Permanently", headers={"Location": path + "/"})
                return
            else:
                # serve index.html within the directory by default
                full_path = full_path / "index.html"
        
        if not full_path.exists():
            self.send_error(404, "Not Found")
            return
        
        content = full_path.read_bytes()
        # get the mime type of the file being served (assume only html and css)
        extension = full_path.suffix.lower()
        mime_type = "application/octet-stream"  # just in case the filetype isn't html or css
        if extension == ".html":
            mime_type = "text/html"
        elif extension == ".css":
            mime_type = "text/css"

        self.wfile.write(f"HTTP/1.1 200 OK\r\n".encode())
        self.wfile.write(f"Content-Length: {len(content)}\r\n".encode())
        self.wfile.write(f"Content-Type: {mime_type}\r\n".encode())
        self.wfile.write(b"Connection: close\r\n")
        self.wfile.write(b"\r\n")
        self.wfile.write(content)        

    def parse_headers(self):
        headers = {}
        while True:
            line = self.rfile.readline().strip().decode('utf-8')
            if not line:
                break
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
        return headers

    def percent_decode(self, string):
        result = []
        i = 0
        while i < len(string):
            char = string[i]
            if char == "%" and i + 2 < len(string): # if we're currently on an encoded character
                hex_val = string[i+1:i+3]   # set the hexadecimal value to be the 2 characters after %
                byte = int(hex_val, 16)     # convert to decimal
                result.append(byte)
                i += 3
            else:
                result.append(ord(char))
                i += 1

        return bytes(result).decode("utf-8")    # turn result into bytes like xc3 and then decode to normal chars

    def send_error(self, code, message, headers=None):
        self.wfile.write(f"HTTP/1.1 {str(code)} {message}\r\n".encode())
        if headers:
            for key, value in headers.items():
                self.wfile.write(f"{key}: {value}\r\n".encode())
        self.wfile.write(f"Content-Length: 0\r\n".encode())
        self.wfile.write(b"Connection: close\r\n")
        self.wfile.write(b"\r\n")

def main():
    # From https://docs.python.org/3/library/socketserver.html, The Python Software Foundation, downloaded 2024-01-07
    with LabHttpTcpServer((HOST,PORT),LabHttpTCPHandler) as server:
        print("server is starting")
        print("running")
        server.serve_forever() 


if __name__ == "__main__":
    main()