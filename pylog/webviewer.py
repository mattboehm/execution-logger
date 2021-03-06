"""A simple web server provides a web interface with visualizations for a log

Usage:
  pylog-web <file>
"""
import json

import docopt
import bottle
import pkg_resources

from pylog import events

class WebViewer(bottle.Bottle):

    def __init__(self, evts):
        super(WebViewer, self).__init__()
        self.evts = evts
        self.route("/", callback=self.root)
        self.route("/flame.json", callback=self.get_flame_json)
        self.route("/static/<filename>", callback=self.static)

    def root(self):
        return bottle.redirect("/static/flame.html")

    def static(self, filename):
        if filename not in pkg_resources.resource_listdir("pylog", "static"):
            bottle.abort(404, "File not found")
        else:
            if filename.endswith(".js"):
                bottle.response.content_type = "text/javascript"
            elif filename.endswith(".css"):
                bottle.response.content_type = "text/css"
            return pkg_resources.resource_string("pylog", "static/" + filename)


    def get_flame_json(self):
        etree = events.ExecutionTree.from_events(self.evts)
        return json.dumps(etree.to_flame_chart(100))

def main():
    options = docopt.docopt(__doc__)
    with open(options["<file>"], "r") as log_file:
        evts = events.events_from_file(log_file)
    
    viewer = WebViewer(evts)
    viewer.run(host="localhost", port=8080)

if __name__ == "__main__":
    main()
