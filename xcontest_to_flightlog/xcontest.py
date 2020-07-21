import requests
from io import BytesIO
import re
import os
from zipfile import ZipFile

from settings import XCONTEST_USERNAME, XCONTEST_PASSWORD, GPSDUMP_FILENAME

def convert_igc_to_kml(fps):
    fps_out = []

    for fp in fps:
        os.system("/app/{} -x{} > /dev/null 2>&1".format(GPSDUMP_FILENAME, fp))
        fps_out.append(fp+".kml")
    
    return fps_out

def extract_zip(input_zip):
    input_zip=ZipFile(input_zip)
    return {name: input_zip.read(name) for name in input_zip.namelist()}

class XContest:
    def __init__(self):
        self.s = requests.Session()
        self.logged_in = False

    def login(self):
        r = self.s.post("https://www.xcontest.org/world/en/",
                  {"login[username]": XCONTEST_USERNAME,
                   "login[password]": XCONTEST_PASSWORD})

        if "Username or password you have entered is not valid!" in r.text:
            raise Exception('XContest user authentication failed')

        if r.status_code == 200:
            self.logged_in = True

    def logout(self):
        r = self.s.get("https://www.xcontest.org/world/en/")
        __x__ = re.search('name="__x__" value="(\w+)\"\/>', r.text).group(1)
        r = self.s.post("https://www.xcontest.org/world/en/", {"__x__": __x__,
                                                               "logout": "::LogOUT::"})
        

    def fetch_xcontest_flights(self, ignore_filenames):
        if not self.logged_in:
            raise Exception('User not authenticated')

        r = self.s.get("https://www.xcontest.org/world/en/my-flights/")
        url = "https://www.xcontest.org" + re.search("(\/util\/export\/igc\/[^\"]+)", r.text).group(1)
        igc_zip = self.s.get(url)
        fps = []
        flights = extract_zip(BytesIO(igc_zip.content))
        for igc in flights:
            if igc in ignore_filenames:
                continue
            fp = "/tmp/" + igc
            fps.append(fp)
        
            with open(fp, "wb") as fo:
                fo.write(flights[igc])

        return fps