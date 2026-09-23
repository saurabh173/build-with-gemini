# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Maps Geocoding and Places (New) tools."""

import json
import os
import urllib.parse
import urllib.request


def geocode_address(address: str) -> str:
    """Converts a street address or location name into geographical coordinates (latitude and longitude).

    Args:
        address: The address or place name to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        Formatted summary with address, latitude, longitude, and place ID.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("status") != "OK" or not data.get("results"):
            return f"Geocoding failed for address '{address}'. Status: {data.get('status')}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address")
        location = result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")
        place_id = result.get("place_id")

        return (
            f"Address: {formatted_address}\n"
            f"Location: Latitude {lat}, Longitude {lng}\n"
            f"Place ID: {place_id}"
        )
    except Exception as e:
        return f"Error during geocoding: {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> str:
    """Finds nearby places of a given type around a latitude/longitude coordinate using Google Places API (New).

    Args:
        latitude: Latitude of the center location.
        longitude: Longitude of the center location.
        place_type: Type of place to search for (e.g., 'restaurant', 'cafe', 'hotel', 'store', 'hospital').
        radius_meters: Search radius in meters (default: 1000.0).

    Returns:
        Formatted summary listing nearby places with name, address, and coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
    }

    payload = {
        "includedTypes": [place_type.lower().strip()],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters,
            }
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        places = data.get("places", [])
        if not places:
            return f"No nearby '{place_type}' places found within {radius_meters} meters of ({latitude}, {longitude})."

        results = []
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown Name")
            address = p.get("formattedAddress", "Unknown Address")
            loc = p.get("location", {})
            lat = loc.get("latitude")
            lng = loc.get("longitude")
            results.append(
                f"• {display_name}\n"
                f"  Address: {address}\n"
                f"  Location: Lat {lat}, Lng {lng}"
            )

        return (
            f"Found {len(places)} nearby '{place_type}' place(s):\n"
            + "\n".join(results)
        )
    except Exception as e:
        return f"Error searching nearby places: {str(e)}"
