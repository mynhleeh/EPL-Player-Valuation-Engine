import requests, argparse, csv
from tabulate import tabulate
from pathlib import Path

API_URL = "http://127.0.0.1:5000/api/search"


# Fetch player databbased on name / club
def fetch_player_data(name, club):
    params = {k: v for k, v in [('name', name), ('club', club)] if v}
    response = requests.get(API_URL, params=params)
    
    if response.ok:
        return response.json()
    
    print("No matching data found.")
    return None


# Display results (summary)
def display_table(data):
    print(" Summary of results: ")

    table_data = [[r.get('Player'), r.get('Squad'), r.get('Nation'), r.get('Pos'), r.get('Age')] for r in data]
    table_view = tabulate(table_data, headers=["NAME", "CLUB", "NATION", "POS", "AGE"], tablefmt="grid")
    
    print(table_view)


# Save to CSV (detailed)
def save_to_csv(data, args):
    path = Path(__file__).resolve().parents[2] / 'data' / 'lookup_ans'

    # Create filename
    file_name = "_".join(p.replace(' ', '_') for p in [args.name, args.club] if p) + ".csv"
    file_path = path / file_name
    
    # Save data to CSV
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader() 
        writer.writerows(data) 
        
    print("Saved detailed stat")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Player lookup tool")
    parser.add_argument("--name", help="Player name")
    parser.add_argument("--club", help="Club name")
    args = parser.parse_args()

    if not args.name and not args.club:
        parser.error("Please provide --name or --club.")
    
    if data := fetch_player_data(args.name, args.club):
        display_table(data)
        save_to_csv(data, args)