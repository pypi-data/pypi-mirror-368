#!/usr/bin/env python3
"""
Test script for the new geographic search functions.
"""
import json
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth using Haversine formula."""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers
    r = 6371
    return c * r


def find_nearest_stations_test(lat: float, lon: float, limit: int = 5):
    """Test version of find_nearest_stations."""
    try:
        with open("uk_tides_mcp/stations.json", "r") as f:
            data = json.load(f)

        stations_with_distance = []

        for feature in data:
            if (
                feature.get("type") == "Feature"
                and "geometry" in feature
                and "properties" in feature
            ):
                geometry = feature["geometry"]
                properties = feature["properties"]

                if geometry.get("type") == "Point" and "coordinates" in geometry:
                    coords = geometry["coordinates"]
                    if len(coords) >= 2:
                        station_lon, station_lat = (
                            coords[0],
                            coords[1],
                        )  # GeoJSON format: [lon, lat]

                        # Calculate distance
                        distance = haversine_distance(
                            lat, lon, station_lat, station_lon
                        )

                        station_info = {
                            "id": properties.get("Id"),
                            "name": properties.get("Name", "Unknown"),
                            "country": properties.get("Country", "Unknown"),
                            "latitude": station_lat,
                            "longitude": station_lon,
                            "distance_km": distance,
                        }
                        stations_with_distance.append(station_info)

        # Sort by distance and return top results
        stations_with_distance.sort(key=lambda x: x["distance_km"])
        return stations_with_distance[:limit]

    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    # Test finding nearest stations to London coordinates
    print("Testing nearest stations to London (51.5074, -0.1278):")
    stations = find_nearest_stations_test(51.5074, -0.1278, 3)
    for station in stations:
        print(f'  {station["name"]} - {station["distance_km"]:.1f}km')

    # Test Cornwall coordinates (near Fowey)
    print("\nTesting nearest stations to Cornwall/Fowey area (50.3352, -4.6365):")
    stations = find_nearest_stations_test(50.3352, -4.6365, 3)
    for station in stations:
        print(f'  {station["name"]} - {station["distance_km"]:.1f}km')
