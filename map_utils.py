import requests
import streamlit as st
INTEREST_TAG = {
    "Nature" : [("natural","peak"),
                   ("natural","waterfall"),
                   ("natural","hill")],
    "Adventure" : [("natural","peak"),
                   ("tourism","attraction"),
                   ("leisure","natural_reserve")],
    "Food": [
        ("amenity", "cafe"),
        ("amenity", "restaurant")
    ],
    "History": [
        ("historic", "monument"),
        ("historic","archaeological_site"),
        ("tourism", "museum")
    ],
    "Photography": [
        ("tourism", "viewpoint"),
        ("natural", "peak")
    ],
    "Nightlife": [
        ("amenity", "bar"),
        ("amenity", "pub"),
        ("amenity", "nightclub")
    ],
    "Shopping": [
        ("shop", "mall"),
        ("shop", "supermarket"),
        ("shop", "clothes"),
        ("shop", "department_store")
    ],
    "Spiritual": [
        ("building", "temple"),
        ("building", "church"),
        ("building", "shrine")
    ]
}
def geocode_location(place):
    url = "https://nominatim.openstreetmap.org/search"
    parameters = {
        "q" : place,
        "format" : "json",
        "limit" : 1,
        "addressdetails": 1
    } 
    response = requests.get(url, params=parameters, headers= {"User-Agent" : "Yatra-Saarthi Student Travel Planner App (educational project)"})

    if response.status_code== 200 and response.json():
        data = response.json()[0]
        country_code = data.get(
            "address",{}
        ).get("country_code", "").lower()
        return float (data["lat"]), float(data["lon"]), country_code
    else :
        return None, None, None
    

def fetch_nearby_attractions(lat, lon, interests, min_results=5):
    
    radii = [5000, 10000, 20000]  # 5km, 10km, 20km

    for radius in radii:
        attractions = fetch_with_radius(lat, lon, interests, radius)
        
        if len(attractions) >= min_results:
            return attractions, radius

    return attractions, radius  # return whatever we got

def fetch_with_radius(lat, lon, interests, radius):

    # Try multiple Overpass servers
    overpass_urls = [
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
        "https://overpass-api.de/api/interpreter"
    ]

    query_parts = []

    # Build dynamic query based on interests
    for interest in interests:
        if interest in INTEREST_TAG:
            for key, value in INTEREST_TAG[interest]:

                query_parts.append(
                    f'node["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

                query_parts.append(
                    f'way["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

                query_parts.append(
                    f'relation["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

    if not query_parts:
        return []

    query_body = "\n".join(query_parts)

    query = f"""
    [out:json];
    (
        {query_body}
    );
    out center;
    """

    # Try each Overpass server
    for overpass_url in overpass_urls:

        try:
            response = requests.post(
                overpass_url,
                data=query,
                timeout=30,
                headers={
                    "User-Agent": "Yatra-Saarthi Student Travel Planner"
                }
            )

            if response.status_code == 200:
                data = response.json()
                break

        except requests.RequestException:
            continue

    else:
        # All servers failed
        return []

    attractions = []
    seen = set()

    for element in data.get("elements", []):

        tags = element.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        # Remove duplicates
        if name in seen:
            continue

        seen.add(name)

        # Get correct coordinates
        if element["type"] == "node":
            lat_val = element.get("lat")
            lon_val = element.get("lon")

        else:
            center = element.get("center", {})
            lat_val = center.get("lat")
            lon_val = center.get("lon")

        if lat_val is None or lon_val is None:
            continue

        attractions.append({
            "name": name,
            "lat": lat_val,
            "lon": lon_val,
            "tags": tags
        })

    return attractions

    overpass_url = "https://overpass-api.de/api/interpreter"

    query_parts = []

    # Build dynamic query based on interests
    for interest in interests:
        if interest in INTEREST_TAG:
            for key, value in INTEREST_TAG[interest]:

                query_parts.append(
                    f'node["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

                query_parts.append(
                    f'way["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

                query_parts.append(
                    f'relation["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

    if not query_parts:
        return []

    query_body = "\n".join(query_parts)

    query = f"""
    [out:json];
    (
        {query_body}
    );
    out center;
    """

    response = requests.post(overpass_url, data=query)

    if response.status_code != 200:
        return []

    data = response.json()
    attractions = []
    seen = set()

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        # Remove duplicates
        if name in seen:
            continue
        seen.add(name)

        # Get correct coordinates
        if element["type"] == "node":
            lat_val = element.get("lat")
            lon_val = element.get("lon")
        else:
            center = element.get("center", {})
            lat_val = center.get("lat")
            lon_val = center.get("lon")

        if lat_val is None or lon_val is None:
            continue

        attractions.append({
            "name": name,
            "lat": lat_val,
            "lon": lon_val,
            "tags": tags
        })

    return attractions