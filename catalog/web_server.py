from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi  # Common Gateway Interface
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant


class webserverHandler(BaseHTTPRequestHandler):
    """Determine what code to execute based on based on HTTP request sent to
    the server"""

    PATTERN_EDIT_RESTAURANT_PATH = r'/restaurants/([0-9]+?)/edit'

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_get_response()

                # Output all restaurants
                restaurant_list = getAllRestaurants()
                output = createHTMLPage(restaurant_list)
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_get_response()

                # Output form to create new restaurant
                form = createNewRestaurantForm()
                output = createHTMLPage(form)
                self.wfile.write(output)
                print output
                return

            if re.search(
                    self.PATTERN_EDIT_RESTAURANT_PATH, self.path) is not None:
                self.send_get_response()

                # Output form to edit existing restaurant based on id from URL
                r_id = re.search(
                    self.PATTERN_EDIT_RESTAURANT_PATH, self.path).group(1)
                form = editRestaurantForm(r_id)
                output = createHTMLPage(form)
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/delete"):
                self.send_get_response()

                # Output form to confirm deletion
                r_id = self.path.split("/")[2]
                form = deleteRestaurantForm(r_id)
                output = createHTMLPage(form)
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File not found at %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('restaurantName')[0]
                    addRestaurant(restaurant_name)

                    self.send_post_response()
                    return

            if re.search(
                    self.PATTERN_EDIT_RESTAURANT_PATH, self.path) is not None:
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    r_name = fields.get('restaurantName')[0]
                    r_id = re.search(
                        self.PATTERN_EDIT_RESTAURANT_PATH, self.path).group(1)
                    editRestaurant(r_id, r_name)

                    self.send_post_response()
                    return

            if self.path.endswith("/delete"):
                r_id = self.path.split("/")[2]
                deleteRestaurant(r_id)

                self.send_post_response()
                return

        except:
            pass

    def send_get_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def send_post_response(self):
        self.send_response(301)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/restaurants')
        self.end_headers()


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


def createDBSession():
    """Connect to database and return session"""
    engine = create_engine('sqlite:///restaurantmenu.db', echo=True)
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def addRestaurant(restaurant_name):
    """Add restaurant to database

    Args:
        restaurant_name: name of restaurant

    """
    session = createDBSession()
    restaurant = Restaurant(name=restaurant_name)
    session.add(restaurant)
    session.commit()


def editRestaurant(r_id, r_name):
    """Edit existing restaurant information in database

    Args:
        r_id: Database ID of restaurant
        r_name: New name for restaurant
    """
    session = createDBSession()
    restaurant = session.query(Restaurant).get(r_id)
    restaurant.name = r_name
    session.commit()


def deleteRestaurant(r_id):
    """Delete restaurant from database

    Args:
        r_id: Restaurant id from database

    """
    session = createDBSession()
    restaurant = session.query(Restaurant).get(r_id)
    session.delete(restaurant)
    session.commit()


def getAllRestaurants():
    """Return an unordered list of all restaurants"""
    session = createDBSession()
    restaurants = session.query(Restaurant).order_by(Restaurant.name).all()

    output = "<ul>"

    for r in restaurants:
        output += "<li><h3 class='margin-b-0'>%s</h3>" % r.name
        output += "<small>"
        output += "<a href='/restaurants/%s/edit'>Edit</a> | " % r.id
        output += "<a href='/restaurants/%s/delete'>Delete</a></small>" % r.id
        output += "</li>"

    output += "</ul><p><a href='/restaurants/new'>Create new restaurant</a></p>"

    return output


def createHTMLPage(content):
    """Creates an HTML page populated with content parameter

    Args:
        content: String of HTMl elements

    """
    output = "<!doctype html><html><head><title>My Restaurant Listings</title>"
    output += "<style>.margin-b-0 { margin-bottom: 0; }</style>"
    output += "</head><body>"
    output += content
    output += "</body></html>"

    return output


def createNewRestaurantForm():
    """Create form for new restaurant"""
    output = ("<form method='POST' enctype='multipart/form-data' "
              "action='/restaurants/new'>"
              "<h2>Create a new restaurant</h2>"
              "<label>Restaurant Name</label>"
              "<input type='text' name='restaurantName'>"
              "<input type='submit' value='Submit'></form>")
    return output


def editRestaurantForm(r_id):
    """Create form to edit existing restaurant

    Args:
        r_id: id extracted from URL

    """
    session = createDBSession()
    restaurant = session.query(Restaurant).get(r_id)

    if restaurant is None:
        output = ("<p>The restaurant you're looking for doesn't exist.<br>"
                  "<a href='/restaurants'>Back to listings</a></p>")
    else:
        output = ("<form method='POST' enctype='multipart/form-data' "
                  "action='/restaurants/%s/edit'>"
                  "<h2>Edit %s restaurant</h2>"
                  "<label>Restaurant Name</label>"
                  "<input type='text' name='restaurantName'>"
                  "<input type='submit' value='Submit'></form>") % (
            restaurant.id, restaurant.name)

    return output


def deleteRestaurantForm(r_id):
    """Create form to delete existing restaurant

    Args:
        r_id: id extracted from URL
    """
    session = createDBSession()
    restaurant = session.query(Restaurant).get(r_id)

    if restaurant is None:
        output = ("<p>The restaurant you're looking for doesn't exist.<br>"
                  "<a href='/restaurants'>Back to listings</a></p>")
    else:
        output = ("<form method='POST' enctype='multipart/form-data' "
                  "action='/restaurants/%s/delete'>"
                  "<h2>Delete %s restaurant</h2><p>Are you sure? "
                  "<input type='hidden' name='restaurantID' value='%s'>"
                  "<input type='submit' value='Delete'></p></form>"
                  "<p><a href='/restaurants'>No, take me back to the listings"
                  "</a></p>") % (restaurant.id, restaurant.name, restaurant.id)

    return output

if __name__ == '__main__':
    main()
