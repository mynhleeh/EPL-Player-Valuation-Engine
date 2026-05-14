from rich.console import Console
from rich.table import Table
from pathlib import Path
from rich import box

import pandas as pd
import argparse
import requests

def get_data(player=None, squad=None):
    url = "http://127.0.0.1:5000/api/search"
    
    params = {}
    if player: params['player'] = player
    elif squad: params['squad'] = squad
    else: return None

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")
        return None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str)
    parser.add_argument("--club", type=str)

    args = parser.parse_args()
    
    if args.name: return get_data(player=args.name), args.name
    elif args.club: return get_data(squad=args.club), args.club
    
    parser.print_help()
    return None, None


def show_results(title, data):
    if not data or not isinstance(data, list) or len(data) == 0:
        print(f"{title} doesn't have data")
        return False

    console = Console()
    table = Table(title=title, box=box.ROUNDED, header_style="bold")

    columns = list(data[0].keys())
    for col in columns: table.add_column(col.capitalize(), justify="left", overflow="fold")

    for d in data:
        row = [str(d.get(col, "")) for col in columns]
        table.add_row(*row)

    console.print(table)


def export_results(title, data):
    base_dir = Path(__file__).resolve().parent.parent.parent
    path = str(base_dir / "data" / "outputs" / (title + ".csv"))

    df = pd.DataFrame(data)
    df.to_csv(path, index=False)


if __name__ == '__main__':
    data, title = parse_args()

    if data is not None:
        show_results(title, data)
        export_results(title, data)
