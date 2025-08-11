import requests
from xml.etree import ElementTree
import numpy as np
from scipy.interpolate import griddata
import sys

def log(message):
    """Utility to log diagnostics to stderr."""
    print(message, file=sys.stderr)

# Function to fetch events from USGS within a time window
def fetch_events(start_time, end_time, min_magnitude=0, max_magnitude=10):
    """
    Fetch earthquake events from the USGS Earthquake API.

    API Documentation:
    https://earthquake.usgs.gov/fdsnws/event/1/

    Args:
        start_time (str): Start time in ISO format (e.g., "2024-01-01").
        end_time (str): End time in ISO format (e.g., "2024-12-01").
        min_magnitude (float): Minimum earthquake magnitude.
        max_magnitude (float): Maximum earthquake magnitude.

    Returns:
        list: List of earthquake events as GeoJSON features.
    """
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start_time,
        "endtime": end_time,
        "minmagnitude": min_magnitude,
        "maxmagnitude": max_magnitude,
    }
    log(f"Querying events from {url} with parameters: {params}")
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["features"]

# Function to fetch ShakeMap XML grid for a specific event
def fetch_shakemap_grid(event_id):
    """
    Fetch the ShakeMap XML grid for a specific event.

    API Documentation:
    https://earthquake.usgs.gov/earthquakes/eventpage/[event_id]/shakemap/grid.xml

    Args:
        event_id (str): The ID of the earthquake event.

    Returns:
        str: XML content of the ShakeMap grid, or None if unavailable.
    """
    xml_url = f"https://earthquake.usgs.gov/earthquakes/eventpage/{event_id}/shakemap/grid.xml"
    log(f"Fetching ShakeMap grid from {xml_url}")
    response = requests.get(xml_url)
    if response.status_code == 200:
        return response.content
    else:
        log(f"No XML grid data available for event {event_id}")
        return None

# Function to extract PGA from XML grid
def get_pga_from_grid(xml_data, latitude, longitude):
    """
    Extract PGA from ShakeMap XML grid at a specific latitude and longitude.

    Args:
        xml_data (str): XML content of the ShakeMap grid.
        latitude (float): Latitude of the desired location.
        longitude (float): Longitude of the desired location.

    Returns:
        float: Interpolated PGA value at the given location, or None if unavailable.
    """
    root = ElementTree.fromstring(xml_data)
    log("Parsing ShakeMap XML grid.")

    # Parse the grid metadata
    nx = int(root.find(".//grid[@name='longitude']").attrib["nrows"])
    ny = int(root.find(".//grid[@name='latitude']").attrib["nrows"])
    lon_min = float(root.find(".//grid[@name='longitude']").attrib["min"])
    lon_max = float(root.find(".//grid[@name='longitude']").attrib["max"])
    lat_min = float(root.find(".//grid[@name='latitude']").attrib["min"])
    lat_max = float(root.find(".//grid[@name='latitude']").attrib["max"])
    
    # Parse the grid data
    grid_values = root.find(".//grid_data").text.strip().split()
    grid_values = np.array(grid_values, dtype=float).reshape((ny, nx))
    
    # Generate grid points
    lons = np.linspace(lon_min, lon_max, nx)
    lats = np.linspace(lat_min, lat_max, ny)
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    # Interpolate PGA at the desired location
    pga = griddata(
        points=(lon_grid.flatten(), lat_grid.flatten()),
        values=grid_values.flatten(),
        xi=(longitude, latitude),
        method="linear",
    )
    if pga is not None:
        log(f"Interpolated PGA at ({latitude}, {longitude}): {pga:.4f} g")
    else:
        log(f"Failed to interpolate PGA at ({latitude}, {longitude}).")
    return pga

# Main script
def main():
    """
    Main script to fetch earthquake events, download ShakeMap grids, and compute PGA.
    """
    # Parameters
    start_time = "2024-01-01"
    end_time = "2024-12-01"
    latitude = 37.7749  # Example location: San Francisco
    longitude = -122.4194

    log(f"Starting process for time window: {start_time} to {end_time}")
    events = fetch_events(start_time, end_time)
    if not events:
        log("No events found in the specified time window.")
        return

    log(f"Found {len(events)} events.")
    for event in events:
        event_id = event["id"]
        event_title = event["properties"]["title"]
        log(f"Processing event: {event_title} (ID: {event_id})")

        xml_data = fetch_shakemap_grid(event_id)
        if xml_data:
            pga = get_pga_from_grid(xml_data, latitude, longitude)
            if pga is not None:
                print(f"Event: {event_title}, PGA at ({latitude}, {longitude}): {pga:.4f} g")
            else:
                print(f"Event: {event_title}, PGA data not available.")
        else:
            print(f"Event: {event_title}, ShakeMap grid data not found.")

if __name__ == "__main__":
    main()

