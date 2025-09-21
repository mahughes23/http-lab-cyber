from sys import argv
import socket

def help():
    print("httpclient.py [GET/POST] [URL] [key1] [value1] [key2] [value2] ...\n")

class HTTPResponse:
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient:
    
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port)) 
        print(f"connected to server at host {host} and port {port}")
        return

    def get_code(self, data):
        status = data.split("\r\n")[0]  # the first line of the response
        code = status.split(" ")[1]     # code comes after the first space
        return int(code)

    def get_headers(self,data):
        headers = {}
        without_body = data.split("\r\n\r\n", 1)[0]         # body comes after \r\n\r\n
        header_lines = without_body.split("\r\n", 1)[1:]    # everything after status line is a header
        for line in header_lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n", 1)
        if len(body) > 1:   # check if body exists
            return body[1]
        return ""
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    
    # Receive the response
    def read_response(self):
        response = b""
        with self.socket.makefile('rb') as sock_file:  
            response = sock_file.read()
        return response

    def GET(self, url, args=None):
        ip, port, path, queries, query_byte_count = self.parse_url(url)
        
        # print(ip)
        # print(port)
        # print(path)
        # print(queries)
        # print(query_byte_count)

        # build the request
        # header
        request = "GET "
        request += ("/" + (path or "") + (queries or "") + " HTTP/1.1\r\n")
        request += ("Host: " + (ip or "") + ":" + str(port or "") + "\r\n")
        request += ("Connection: close\r\n")    # close the port as per the hints
        request += "\r\n"   # headers end with a blank line

        # no body (because it's GET)

        self.connect(ip, port)
        self.socket.sendall(request.encode("utf-8"))
        response_bytes = self.read_response()
        response_str = response_bytes.decode("utf-8")
        self.close()

        code = self.get_code(response_str)
        body = self.get_body(response_str)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        ip, port, path, queries, query_byte_count = self.parse_url(url)
        
        # print(ip)
        # print(port)
        # print(path)
        # print(queries)
        # print(query_byte_count)

        # build the request
        # header
        request = "POST "
        request += ("/" + (path or "") + (queries or "") + " HTTP/1.1\r\n")
        request += ("Host: " + (ip or "") + ":" + str(port or "") + "\r\n")
        request += ("Connection: close\r\n")    # close the port as per the hints
        if queries is not None:
            request += ("Content-Type: application/x-www-form-urlencoded\r\n")
            request += ("Content-Length: " + str(query_byte_count) + "\r\n")
        request += "\r\n"   # headers end with a blank line

        # body
        unencoded_query = url.split("?", 1)[1]  # split once, the second half is the query
        print("body: " + unencoded_query)

        self.connect(ip, port)
        self.socket.sendall(request.encode("utf-8"))
        response_bytes = self.read_response()
        response_str = response_bytes.decode("utf-8")
        self.close()
        
        code = self.get_code(response_str)
        body = self.get_body(response_str)
        
        return HTTPResponse(code, body)

    def parse_url(self, url):
        no_protocol = url.split("//")
        ip_and_port, path_and_queries = no_protocol[1].split("/", 1)
        
        ip = None
        port = None
        if "]" in ip_and_port:  # if IPv6, split it by the closed bracket
            ip, port = ip_and_port.split("]", 1)
            ip = ip[1:]     # remove the first "[" to isolate the ip
            port = port[1:] # remove the left-over ":" to isolate the port
            if port == "":   # if port is empty, set it to default value of 80
                port = 80
            else:
                pass
                # port = int(port)    # convert it to an int
        else:   # IPv4
            if ":" in ip_and_port:  # if there's a port separator
                ip, port = ip_and_port.split(":")
            else:
                ip = ip_and_port
                port = 80   # default

        path = None
        queries = None
        if "?" in path_and_queries:     # if there are any specified queries
            path, queries = path_and_queries.split("?", 1)
        else: 
            path = path_and_queries

        query_byte_count = 0
        if path:
            path = self.percent_encode(path)[0]
        if queries:
            queries, query_byte_count = self.percent_encode(queries)

        # convert port to int
        port = int(port)

        parsed_url = [ip, port, path, queries, query_byte_count]
        return parsed_url

    def percent_encode(self, string):
        result = []
        byte_count = 0
        for char in string:
            if (char in "-_./") or "A" <= char <= "Z" or "a" <= char <= "z" or "0" <= char <= "9":   # we don't want to encode these
                result.append(char) # add the normal char to the result
            else:
                # encode the char
                for byte in char.encode("utf-8"):   # will parse "é" as xc3 xc9 for example
                    result.append(f"%{byte:02X}")   # set the format to uppercase hexadecimal with 2 digits
            byte_count += 1
        return ["".join(result), byte_count]
    
    def command(self, command, url, args):
        assert isinstance(url, str)
        assert isinstance(args, dict)
        if command == "POST":
            return  self.POST(url, args)
        elif command == "GET":
            return  self.GET(url, args)
        else:
            raise ValueError("not get or post")
    


if __name__ == "__main__":
    client = HTTPClient()
    if len(argv) < 3:
        help()
    else:
        method = argv[1]
        url = argv[2]
    key = None
    args = dict()
    for arg in argv[3:]:
        if key is None:
            key = arg
        else:
            args[key] = arg
            key = None
    if key is not None:
        args[key] = ""
    result = client.command(method, url, args)
    print("Response code:", result.code)
    print("Response body:")
    print(result.body)