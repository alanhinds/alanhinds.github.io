# Leaflet cluster map of talk locations
#
# Run this from the _talks/ directory, which contains .md files of all your
# talks. This scrapes the location YAML field from each .md file, geolocates it
# with geopy/Nominatim, and uses the getorg library to output data, HTML, and
# Javascript for a standalone cluster map. This is functionally the same as the
# #talkmap Jupyter notebook.
import frontmatter
import glob
import getorg
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

# Set the default timeout, in seconds
TIMEOUT = 5

# Collect the Markdown files
g = glob.glob("_talks/*.md")

# Prepare to geolocate
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}
location = ""
permalink = ""
title = ""

# Perform geolocation
for file in g:
    # Read the file
    data = frontmatter.load(file)
    data = data.to_dict()

    # Press on if the location is not present
    if 'location' not in data:
        continue

    # Prepare the description
    title = data['title'].strip()
    venue = data['venue'].strip()
    location = data['location'].strip()
    description = f"{title}<br />{venue}; {location}"

    # Geocode the location and report the status
    try:
        location_dict[description] = geocoder.geocode(location, timeout=TIMEOUT)
        print(description, location_dict[description])
    except ValueError as ex:
        print(f"Error: geocode failed on input {location} with message {ex}")
    except GeocoderTimedOut as ex:
        print(f"Error: geocode timed out on input {location} with message {ex}")
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {location} with message {ex}")

# Save the map
m = getorg.orgmap.create_map_obj()
getorg.orgmap.output_html_cluster_map(location_dict, folder_name="talkmap", hashed_usernames=False)


# Re-center the generated map over the continental U.S. instead of getorg's
# default world view, since getorg doesn't expose center/zoom as a parameter.
map_html_path = "talkmap/map.html"
with open(map_html_path, "r") as f:
    map_html = f.read()

map_html = map_html.replace(
    "latlng = L.latLng(30, 10);", "latlng = L.latLng(39.8, -98.6);"
).replace(
    "zoom: 0.7", "zoom: 3"
).replace(
    "maxClusterRadius: 80", "maxClusterRadius: 30"
).replace(
    "<span>Mouse over a cluster to see the bounds of its children and click a cluster to zoom to those bounds</span>",
    '<p style="font-size: smaller; color: var(--global-text-color-light);">Click a cluster to zoom in and see the individual talks.</p>'
)

with open(map_html_path, "w") as f:
    f.write(map_html)