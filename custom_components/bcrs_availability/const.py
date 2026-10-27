"""Constants for BCRS Availability."""

from datetime import timedelta

DOMAIN = "bcrs_availability"

CONF_PLACE = "place"

# How far from the saved coordinates to look for the machine on each update.
SEARCH_RADIUS_M = 100
# Please keep this polite: the API belongs to a public website.
SCAN_INTERVAL = timedelta(minutes=5)

# How many matches the setup dialog lists.
MAX_NAME_MATCHES = 50
MAX_NEARBY_MATCHES = 10
