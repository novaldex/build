#!/usr/bin/python

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import re
import urllib
import os

files = {}

class PackageHandler(ContentHandler):
    getData = 0
    url = ""
    filename = ""
    json = ""
    author = ""
    screenshots = []

    def startElement(self, name, attrs):
        if (name == "application") :
            self.json = "{ "
            self.author = ""
            self.screenshots = []

        self.getData = 1
        self.data = ""
            
    def endElement(self,name):
        self.getData = 0

        if (name == "title") :
            self.json += "\"Title\":\"%s\", " % self.data

        if (name == "lastupdate") :
            self.json += "\"LastUpdated\":\"%s\", " % self.data

        if (name == "icon") :
            self.json += "\"Icon\":\"%s\", " % self.data

        if (name == "license") :
            self.json += "\"License\":\"%s\", " % self.data

        if (name == "description") :
            self.json += "\"FullDescription\":\"%s\", " % self.data

        if (name == "categories") :
            self.json += "\"Type\":\"Application\", "
            self.json += "\"Category\":\"%s\", " % self.data

        if (name == "author") :
            self.author = self.data

        if (name == "link") :
            self.json += "\"Homepage\":\"%s\", " % self.data.replace("homebrew-apps/homebrew-apps","homebrew-apps")

        if (name == "url") :
            self.url = self.data

        if (name == "screenshot") :
            self.screenshots.append('"' + self.data + '"')

        if (name == "application") :

            regexp = re.compile("^(.*)/([^/]+.ipk)")
            m = regexp.match(self.url)
            if (m):
                self.filename = m.group(2)

                if (len(self.screenshots)):
                    self.json += "\"Screenshots\":[" + ','.join(self.screenshots) + "], "

                self.json += "\"Feed\":\"PreCentral\" }"

                print "Filename: " + self.filename
                print "Source: " + self.json
                if (self.author):
                    print "MaintainerURL: " + "http://forums.precentral.net/members/" + urllib.quote(self.author) + ".html"

                if (not os.path.exists(sys.argv[2] + "/" + self.filename)) :
                    sys.stderr.write("Fetching: " + self.filename + "\n")
                    os.system("curl -R -L -o " + sys.argv[2] + "/" + self.filename + " " + self.url)

                files[self.filename] = 1

                print

        return

    def characters (self, ch): 
        if (self.getData) :
            self.data += ch.encode('utf-8').replace('"', '\\"').replace(': ', '&#58; ').replace('\r', '').replace('\n', '')

        return

feedprint = PackageHandler()
saxparser = make_parser()
saxparser.setContentHandler(feedprint)
                        
datasource = open(sys.argv[1],"r")
saxparser.parse(datasource)

for f in os.listdir(sys.argv[2]):
    if (not files.has_key(f)):
        sys.stderr.write(sys.argv[2] + "/" + f + "\n")
        os.remove(sys.argv[2] + "/" + f)
