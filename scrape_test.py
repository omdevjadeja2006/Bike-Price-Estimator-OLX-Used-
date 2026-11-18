from curl_cffi import requests

# The live OLX endpoint you captured
url = "https://api.olx.in/relevance/v4/search"

params = {
    "category": "2198",
    "facet_limit": "1000",
    "location": "4058723",
    "location_facet_limit": "40",
    "platform": "web-desktop",
    "pttEnabled": "true",
    "relaxedFilters": "true",
    "size": "40",
    "user": "anonymous",
    "lang": "en-IN"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.olx.in/motorcycles_c81"
}

print("Connecting to live OLX API via Chrome impersonation...")

try:
    # impersonate="chrome" forces the TLS handshake to mimic Google Chrome
    response = requests.get(
        url, 
        params=params, 
        headers=headers, 
        impersonate="chrome", 
        timeout=10
    )
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        items = data.get("data", [])
        print(f"Success! Retrieved {len(items)} vehicle listings from Rajkot.\n")

        if items:
            first_bike = items[0]
            print(first_bike)
            print("--- FIRST LISTING RECORD ---")
            print("Title:", first_bike.get("title"))
            print("Price:", first_bike.get("price", {}).get("value", {}).get("display"))
            print("Location:", first_bike.get("locations_resolved", {}).get("ADMIN_LEVEL_3_name"))
    else:
        print("Server error:", response.status_code)

except Exception as e:
    print("Execution Error:", e)