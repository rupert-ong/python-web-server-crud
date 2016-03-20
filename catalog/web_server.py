from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi  # Common Gateway Interface


class webserverHandler(BaseHTTPRequestHandler):
    """Determine what code to execute based on based on HTTP request sent to
    the server"""
    pass


def main():
    """Instantiate the web server with address and port number"""
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered. Stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
