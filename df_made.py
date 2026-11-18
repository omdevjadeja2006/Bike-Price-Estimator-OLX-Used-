import time
import pandas as pd
from curl_cffi import requests

# Base Setup
url = "https://api.olx.in/relevance/v4/search"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.olx.in/motorcycles_c81"
}

all_bikes = []
total_pages = 200  # Up to 600 listings (15 * 40)

print(f"Starting extraction across {total_pages} pages...")

for page in range(0, total_pages):
    print(f"Fetching page {page + 1}/{total_pages}...")
    
    params = {
        "category": "2198",
        "facet_limit": "1000",
        "location": "2001154",
        "location_facet_limit": "40",
        "platform": "web-desktop",
        "pttEnabled": "true",
        "relaxedFilters": "true",
        "size": "40",
        "page": str(page),
        "user": "anonymous",
        "lang": "en-IN"
    }

    try:
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            impersonate="chrome", 
            timeout=10
        )

        if response.status_code == 200:
            raw_data = response.json()
            items = raw_data.get("data", [])
            
            if not items:
                print(f"No more data returned at page {page + 1}. Ending loop.")
                break

            for item in items:
                title = item.get("title", "N/A")
                price = item.get("price", {}).get("value", {}).get("raw", None)
                city = item.get("locations_resolved", {}).get("ADMIN_LEVEL_3_name", "N/A")
                area = item.get("locations_resolved", {}).get("SUBLOCALITY_LEVEL_1_name", "N/A")

                raw_params = item.get("parameters", [])
                param_dict = {
                    p.get("key_name"): p.get("formatted_value") 
                    for p in raw_params if p.get("key_name")
                }

                brand = param_dict.get("Brand", "N/A")
                model = param_dict.get("Model", "N/A")
                year_str = param_dict.get("Year", None)
                km_raw = param_dict.get("KM driven", "0")

                year = int(year_str) if year_str and year_str.isdigit() else None
                km_clean = "".join(filter(str.isdigit, str(km_raw)))
                km_driven = int(km_clean) if km_clean else None

                all_bikes.append({
                    "Title": title,
                    "Brand": brand,
                    "Model": model,
                    "Year": year,
                    "KM_Driven": km_driven,
                    "Price": price,
                    "Area": area,
                    "City": city
                })

            print(f"--> Extracted {len(items)} items from page {page + 1}")

        else:
            print(f"Failed page {page + 1}. Status Code: {response.status_code}")
            break

    except Exception as e:
        print(f"Error on page {page + 1}: {e}")
        break

    # Pacing delay to avoid blocking
    time.sleep(2.5)

# Save and Export
df = pd.DataFrame(all_bikes)
df = df.drop_duplicates(subset=["Brand", "Model", "Year", "KM_Driven", "Price"])

print(f"\nExtraction complete! Total unique records: {len(df)}")

output_filename = "olx_bikes_dataset.csv"
df.to_csv(output_filename, index=False)
print(f"Dataset saved to: {output_filename}")