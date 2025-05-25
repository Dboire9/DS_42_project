import os
import sys
import dotenv
import requests
import csv

def main():
    dotenv.load_dotenv()
    UID = os.getenv('UID')
    SECRET = os.getenv('SECRET')
    
    # Get an access token
    response = requests.post(
        "https://api.intra.42.fr/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": UID,
            "client_secret": SECRET,
        }
    )
    token = response.json().get("access_token")
    # print(token)
    
    headers = {"Authorization": f"Bearer {token}"}
    all_cursus_users = []
    page = 3001
    page_nb = 3500
    while page <= page_nb:
        response = requests.get(
            "https://api.intra.42.fr/v2/locations",
            headers=headers,
            params={"page[number]": page, "page[size]": 100}
        )
        cursus_users = response.json()
        if not cursus_users or not isinstance(cursus_users, list):
            continue
        if 'errors' in cursus_users:
            print(f"Error on page {page}: {cursus_users['errors']}")
            continue
        all_cursus_users.extend(cursus_users)
        print_progress(page, page_nb)
        page += 1
    
    csv_file = "locations.csv"
    write_header = not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0

    if all_cursus_users:
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_cursus_users[0].keys())
            if write_header:
                writer.writeheader()
            writer.writerows(all_cursus_users)
        print(f"Appended {len(all_cursus_users)} cursus_users.")
    else:
        print("No cursus_users found.")

def print_progress(current, total, bar_length=40):
    percent = float(current) / total
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f"\rProgress: [{arrow}{spaces}] {current}/{total} pages")
    sys.stdout.flush()

if __name__ == "__main__":
    main()