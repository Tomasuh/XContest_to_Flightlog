# XContest to Flightlog automation script

This dockerized python script pulls the given user's IGC files from XContest, converts them to kml format with the help of Gpsdump and then submits them to flightlog.org if it does not already exist there.

## Setup

Create a `.env` file in the root directory of the project with the following entries:

```
XCONTEST_USERNAME=myusername
XCONTEST_PASSWORD=BV0==mypassword
FLIGHTLOG_USERNAME=myusername
FLIGHTLOG_PASSWORD=mypassword
FLIGHTLOG_BRANDMODEL_ID=my_brandmodel
DEFAULT_TAKEOFF_TYPE=2
```

Build it:

```
docker-compose build
```

Run it:

```
docker-compose up
```

### Remarks `FLIGHTLOG_BRANDMODEL_ID`
Can be found in the html of the `New flight` page located at `https://flightlog.org/fl.html?l=1&user_id=7216&a=30&no_start=y`. Search for `brandmodel_id` in the html and take the integer value of the `value` field.

### Remarks `DEFAULT_TAKEOFF_TYPE`

Flightlog does not support takeoff type for flight spots, instead one selects it for each entry. I went for the lazy solution and let the user hardcode the default takeoff type to use.

* 1 is for mountain
* 2 is for coastal soaring
* 3 is for towing


