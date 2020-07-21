import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import re
from settings import FLIGHTLOG_USERNAME, FLIGHTLOG_PASSWORD, FLIGHTLOG_BRANDMODEL_ID, DEFAULT_TAKEOFF_TYPE

class Flightlog:
    def __init__(self):
        self.logged_in = False
        self.user_id = None
        self.entries = {}
        self.s = None

    def login(self):
        self.s = requests.Session()
        data_form = {"form": "login", 
                     "url": "", 
                     "login_name":FLIGHTLOG_USERNAME, 
                     "pw": FLIGHTLOG_PASSWORD, 
                     "login": "Login"}

        r = self.s.post("https://flightlog.org/fl.html?l=1&a=37", data=data_form)

        if r.status_code == 200 and "Couldn't find the username" not in r.text:
            self.logged_in = True

        else:
            raise Exception('Failed to authenticate to Flightlog')

        self.user_id = r.url.split("=")[-1]

    def logout(self):
        self.s.get("https://flightlog.org/fl.html?l=1&a=38")

    def index_flights(self):
        if not self.logged_in:
            raise Exception("Flightlog user not authenticated")

        r = self.s.get("https://flightlog.org/fl.html?l=1&a=28&user_id={}".format(self.user_id))

        res = re.findall("<tr>.+?</tr>", r.text,flags = re.DOTALL)
        for match in res:
            if "&trip_id=" not in match:
                continue 

            date = re.search("(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}<br>", match)
            
            # Happens when no tracklog is in the entry
            if not date:
                continue

            date = date.group(1)
            trip_id = re.search("&trip_id=(\d+)'", match).group(1)

            if date not in self.entries:
                self.entries[date] = []

            self.entries[date].append(trip_id)

    # date_str should be formatted as: "2020-06-09"
    # time_duration as "15:51:22 - 17:57:04"
    # Returns true if matching entry found
    def flight_registered(self, date_str, time_duration):
        if date_str in self.entries:
            for trip_id in self.entries[date_str]:
                flight_url = "https://flightlog.org/fl.html?a=34&user_id={}&trip_id={}".format(self.user_id, trip_id)
                r = self.s.get(flight_url)
                if "Start/finish         " + time_duration in r.text:
                    return True

        return False

    def register_flight(self, tracklog_fp, country_name, cordinates):
        if not self.logged_in:
            raise Exception("Flightlog user not authenticated")
        
        multipart_form_data = {
            "form": "trip_form",
            "trip_id": None,
            "timestamp": None,
            "locked": None,
            "country_id": None,
            "start": None,
            "tripdate_day": None,
            "tripdate_month": None,
            "tripdate_year": None,
            "triptime_h": None,
            "triptime_m": None,
            "takeofftype_id": DEFAULT_TAKEOFF_TYPE,
            "class_id": "1",
            "brandmodel_id": FLIGHTLOG_BRANDMODEL_ID,
            "brandmodel": None,
            "cnt": "0",
            "duration_h": None,
            "duration_m": None,
            "distance": None,
            "maxaltitude": None,
            "url": None,
            "description": "Imported with XContest_to_Flightlog tool (https://github.com/Tomasuh/XContest_to_Flightlog)",
            "private": None,
            "tracklog": (tracklog_fp.split("/")[-1], open(tracklog_fp, "rb"), "application/vnd.google-earth.kml+xml"),
            "image": None,
            "save": "Save"
        }
        multipart_form_data_obj = MultipartEncoder(multipart_form_data)

        res = self.s.post("https://flightlog.org/fl.html?l=1&user_id={}&a=30&no_start=y".format(self.user_id),
            data=multipart_form_data_obj,
            headers={'Content-Type': multipart_form_data_obj.content_type})

        if (res.status_code == 200 and 
            "When you don't specify a registered takeoff, you have to describe the place or places this flight or group of flight took place." in res.text):

            generated_launch_name = "{}: Launch cordinates {}".format(country_name, cordinates)
            print("Failed to find a matching launch, setting '{}'.".format(generated_launch_name))

            country_id = re.search("<option value='(\d+)'>{}".format(country_name), res.text).group(1)
            multipart_form_data["country_id"] = country_id
            multipart_form_data["start"] = generated_launch_name
            multipart_form_data["tracklog"] = (tracklog_fp.split("/")[-1], open(tracklog_fp, "rb"), "application/vnd.google-earth.kml+xml")

            multipart_form_data_obj = MultipartEncoder(multipart_form_data)

            res = self.s.post("https://flightlog.org/fl.html?l=1&user_id={}&a=30&no_start=y".format(self.user_id),
                data=multipart_form_data_obj,
                headers={'Content-Type': multipart_form_data_obj.content_type})



