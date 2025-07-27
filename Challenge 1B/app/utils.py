import json
from pathlib import Path
from datetime import datetime

def load_input_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_output_json(output, test_case_name):
    out_dir = Path("app/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"{test_case_name}.json", "w") as f:
        json.dump(output, f, indent=4)