import argparse
import pandas as pd
from .main import df_desc, df_stats, df_nullique, sanitize_for_excel
from pathlib import Path

# Function to normalize excel suffix
def _xlsx_this(path: Path) -> Path:
    return path.with_suffix(".xlsx")

# Function to dynamically check the flags and validate them
def _check_flags(p: argparse.ArgumentParser):
    flags = []
    for i in p._actions:
        input_flags = [j for j in i.option_strings if j.startswith("--")]
        if not input_flags:
            continue
        if i.dest in ("help"):
            continue
        flags.append((i.dest, input_flags[0]))
    return flags

def main():
    parser = argparse.ArgumentParser(description="Run df-this on an Excel file.")
    parser.add_argument("input_file", type=str, help="Path to the input Excel file")
    parser.add_argument("output_file", nargs="?", type=str, help="Path to save the output Excel file (defaults to <input_path>_df-this.xlsx)", default=None)

    # Activate the df_desc function with --desc
    parser.add_argument("--desc",action="store_true",help="Run 'df-this <input> <output> --desc' to find out the content of each column.")

    # Activate the df_stats function with --stat
    parser.add_argument("--stat",action="store_true",help="Run 'df-this <input> <output> --stat' to see basic statistics for each column.")

    # Activate the df_nullique function with --null
    parser.add_argument("--null",action="store_true",help="Run 'df-this <input> <output> --null' to see if the column is distinct, get the distinct count, and see if there are null values.")

    # Activate all functions as added sheets with the original table with --all
    parser.add_argument("--all",action="store_true",help="Run 'df-this <input> <output> --all' to get all functions as additional sheets in a copy of the original file.")

    args = parser.parse_args()

    checked_flags = _check_flags(parser)
    flag_state = {dest:bool(getattr(args, dest)) for dest, _ in checked_flags}
    if not any(flag_state.values()):
        options = ", ".join(opt for _, opt in checked_flags)
        parser.error(f"Honestly, this would be much easier if you gave me at least one of: {options}")

    input_path = Path(args.input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"OI! Where's my input file?! {input_path}")
    
    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_df-this.xlsx"
    output_path = _xlsx_this(Path(output_path))

    df = pd.read_excel(input_path, engine="openpyxl")

    # What to do?
    run_desc = args.desc
    run_stat = args.stat
    run_null = args.null

    if args.all:
        run_desc = run_stat = run_null = True
    
    # Execute the tasks
    results = []
    if run_desc:
        results.append(("description", df_desc(df)))
    if run_stat:
        results.append(("stats", df_stats(df)))
    if run_null:
        results.append(("nulls", df_nullique(df)))
    
    if len(results) == 1:
        name, final_df = results[0]
        out_df = sanitize_for_excel(final_df)
        out_df.to_excel(output_path, index=False)
        print(f"df-this saved {name} - {input_path} to {output_path}")
    else:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Old_df")
            for name, final_df in results:
                out_df = sanitize_for_excel(final_df)
                out_df.to_excel(writer, index=False, sheet_name=name[:31])
        print(f"df-this saved all - {input_path} to {output_path}")