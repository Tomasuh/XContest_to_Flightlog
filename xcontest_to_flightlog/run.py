import requests
import sys
import re
import os
import pycountry
from geopy.geocoders import Nominatim

from settings import GPSDUMP_FILENAME, XCONTEST_USERNAME, XCONTEST_PASSWORD, FLIGHTLOG_USERNAME, FLIGHTLOG_PASSWORD
from xcontest import XContest, convert_igc_to_kml
from flightlog import Flightlog

def find_kml_time_details(fp):
    with open(fp, "r") as f:
        content = f.read()

    date = re.search("Date                 (\d{4}-\d{2}-\d{2})", content).group(1)
    time_interval = re.search("Start\/finish         (\d{2}:\d{2}:\d{2} - \d{2}:\d{2}:\d{2})", content).group(1)

    cordinates = re.search("<coordinates>\n\s*(\d+\.\d+,\d+\.\d+),\d+\n", content).group(1)

    splitted = cordinates.split(",")
    splitted.reverse()
    cordinates = ",".join(splitted)
    geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
    location = geolocator.reverse(cordinates)

    cc = location.raw['address']['country_code']
    english_country_name = pycountry.countries.get(alpha_2=cc.upper()).name

    return (date, time_interval, english_country_name, cordinates)


def main():
    if not os.path.exists("/storage/handled_logfiles.txt"):
        os.mknod("/storage/handled_logfiles.txt")

    with open("/storage/handled_logfiles.txt") as f:
        handled_logfiles = [line.rstrip() for line in f.readlines()]

    xc = XContest()
    print("Authenticating to XContest")
    xc.login()
    print("Fetching XContest flights")
    fps = xc.fetch_xcontest_flights(handled_logfiles)
    if len(fps) == 0:
        print("Found no new XContest flights to handle, exiting.")
        sys.exit()

    print("Downloaded {} new flights from XContest, converting them to kml with gpsdump.".format(len(fps)))
    fps_kml = convert_igc_to_kml(fps)

    print("Logging out from XContest")
    xc.logout()
    fl = Flightlog()

    print("Authenticating to Flightlog and indexing flights")
    fl.login()
    fl.index_flights()

    f = open("/storage/handled_logfiles.txt", "a")
    for fp in fps_kml:
        date, time_interval, country_name, cordinates = find_kml_time_details(fp)
        registered = fl.flight_registered(date, time_interval)

        if registered:
            print("Flight happening at {} {} already uploaded to Flightlog, ignoring".format(date, time_interval))
        else:
            print("Found flight at {} {} not to be at Flightlog, uploading it".format(date, time_interval))
            fl.register_flight(fp, country_name, cordinates)

        f.write(fp.split("/")[-1][:-4] + "\n")

    f.close()

    print("Logging out from Flightlog")
    fl.logout()
    print("Done")

main()