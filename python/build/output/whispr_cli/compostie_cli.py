import csv
from tabulate import tabulate

def load_latest_scores(path="logs/whispr_edge_composites.csv"):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def print_top_scores(n=10):
    data = load_latest_scores()
    data = sorted(data, key=lambda x: float(x[2]), reverse=True)
    table = [[row[1], row[2], row[3]] for row in data[:n]]
    print(tabulate(table, headers=["Ticker", "Score", "Explanation"]))

if __name__ == "__main__":
    print_top_scores()
