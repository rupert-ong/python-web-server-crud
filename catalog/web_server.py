from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi  # Common Gateway Interface

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant


class webserverHandler(BaseHTTPRequestHandler):
    """Determine what code to execute based on based on HTTP request sent to
    the server"""
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Output all restaurants
                restaurant_list = getAllRestaurants()
                output = createHTMLPage(restaurant_list)

                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File not found at %s" % self.path)


def createDBSession():
    """Connect to database and return session"""
    engine = create_engine('sqlite:///restaurantmenu.db', echo=True)
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def getAllRestaurants():
    """Return an unordered list of all restaurants"""
    session = createDBSession()
    restaurants = session.query(Restaurant).order_by(Restaurant.name).all()

    output = "<ul>"

    for r in restaurants:
        output += "<li><h3>%s</h3>" % r.name
        output += "<small><a href='#'>Edit</a> | <a href='#'>Delete</a></small>"
        output += "</li>"

    output += "</ul>"

    return output


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


def createHTMLPage(content):
    """Creates an HTML page populated with content parameter

    Args:
        content: String of HTMl elements

    """
    output = "<!doctype html><html><head></head><body>"
    output += content
    output += "</body></html>"

    return output

if __name__ == '__main__':
    main()
