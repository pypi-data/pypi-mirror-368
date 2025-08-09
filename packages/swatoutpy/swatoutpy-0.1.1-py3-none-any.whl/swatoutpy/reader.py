
from pathlib import Path
from datetime import datetime
import os
import pandas as pd
from swatoutpy.utils import get_column_names, get_column_widths


def read_rch(filepath: str, timestep: str = "monthly") -> pd.DataFrame:
    """
    Read SWAT2020 (v681) .rch output and return a cleaned DataFrame.
    Always includes a Date column.

    Parameters:
    - filepath: Path to .rch file
    - timestep: 'monthly' or 'annual'

    Returns:
    - df: pandas DataFrame with Date column
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"{filepath} does not exist.")

    columns = get_column_names()["rch"]
    df = pd.read_csv(filepath, sep=r"\s+", skiprows=9, header=None, engine="python")
    df.columns = columns

    n_reaches = df["RCH"].nunique()

    # Drop final summary rows (1 per reach)
    df = df.iloc[:-n_reaches].copy()

    if timestep.lower() == "monthly":
        # Detect simulation years from annual rows
        year_rows = df[df["MON"] > 12]
        sim_years = sorted(year_rows["MON"].unique())
        if not sim_years:
            raise ValueError("No simulation years found in MON > 12.")

        start_year = int(sim_years[0])

        # Remove annual rows
        df = df[df["MON"] <= 12].copy().reset_index(drop=True)

        # Build date list
        n_months = len(df) // n_reaches
        date_list = []
        year, month = start_year, 1
        for _ in range(n_months):
            date_list.extend([datetime(year, month, 1)] * n_reaches)
            month += 1
            if month > 12:
                month = 1
                year += 1

        if len(date_list) != len(df):
            raise ValueError(f"Expected {len(df)} dates, got {len(date_list)}.")

        df["Date"] = pd.to_datetime(date_list)

    elif timestep.lower() == "annual":
        annual_df = df[df["MON"] > 12].copy()
        annual_df["Date"] = pd.to_datetime(annual_df["MON"].astype(int).astype(str), format="%Y")
        df = annual_df

    else:
        raise ValueError("timestep must be 'monthly' or 'annual'.")

    # Keep Date as column (do NOT set as index here)
    return df



def read_sub(filepath: str, timestep: str = "monthly") -> pd.DataFrame:
    """
    Read SWAT2020 .sub output (monthly or annual) with fixed-width parsing and
    return a DataFrame that ALWAYS includes a real datetime "Date" column.
    - Monthly: Date = first day of each month
    - Annual:  Date = Jan 1 of each year

    Also drops the final long-term summary block (1 row per SUB) if present.
    """
    fp = Path(filepath)
    if not fp.exists():
        raise FileNotFoundError(f"{fp} does not exist.")

    # 1) Find data start (line after header row that begins with 'SUB')
    with fp.open("r") as f:
        lines = f.readlines()
    start_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("SUB"):
            start_line = i + 1
            break

    # 2) Column names & widths
    colnames = get_column_names()["sub"]
    widths   = get_column_widths()["sub"]
    if len(widths) != len(colnames):
        raise ValueError("Mismatch in number of widths and column names for .sub")

    # 3) Read fixed-width data
    df = pd.read_fwf(fp, skiprows=start_line, names=colnames, widths=widths)

    # 4) Basic types and sanity
    if "SUB" not in df.columns or "MON" not in df.columns:
        raise KeyError("Expected columns 'SUB' and 'MON' not found in .sub file.")
    df["SUB"] = df["SUB"].astype(int)
    n_subs = df["SUB"].nunique()

    # 5) Drop final long-term summary block (1 row per SUB at the very end) if present
    tail = df.tail(n_subs)
    if len(tail) == n_subs and (tail["MON"] > 12).all():
        df = df.iloc[:-n_subs].copy()

    # 6) Detect simulation years from annual rows (MON > 12)
    annual_rows = df[df["MON"] > 12].copy()
    if annual_rows.empty:
        raise ValueError("Could not detect annual summary rows (MON > 12).")
    sim_years = sorted(annual_rows["MON"].astype(int).unique())
    if not sim_years:
        raise ValueError("No simulation years detected from annual rows.")

    if timestep.lower() == "monthly":
        # Keep only monthly rows
        monthly = df[df["MON"] <= 12].copy().reset_index(drop=True)

        # Ensure row count is a multiple of n_subs; trim any ragged tail
        if len(monthly) % n_subs != 0:
            monthly = monthly.iloc[: len(monthly) - (len(monthly) % n_subs)].copy()

        # Expected number of monthly chunks
        expected_chunks = len(sim_years) * 12
        n_chunks = min(expected_chunks, len(monthly) // n_subs)

        # Build ordered dates: year-major, then month 1..12
        all_dates = [datetime(y, m, 1) for y in sim_years for m in range(1, 13)]
        all_dates = all_dates[:n_chunks]

        # Assign dates WITHOUT reordering rows: one date per n_subs-sized chunk
        monthly = monthly.iloc[: n_chunks * n_subs].copy()
        monthly["Date"] = [all_dates[i // n_subs] for i in range(len(monthly))]

        # Return with Date column (and keep MON for debugging if you like)
        monthly["Date"] = pd.to_datetime(monthly["Date"])
        # monthly = monthly.set_index("Date")  # <- enable if you prefer Date as index
        return monthly

    elif timestep.lower() == "annual":
        # Keep only annual rows, and only those that correspond to sim_years
        annual = annual_rows[annual_rows["MON"].isin(sim_years)].copy().reset_index(drop=True)

        # Trim to full years * subs if there’s any excess
        expected_rows = len(sim_years) * n_subs
        if len(annual) > expected_rows:
            annual = annual.iloc[:expected_rows].copy()

        annual["Date"] = pd.to_datetime(annual["MON"].astype(int).astype(str), format="%Y")
        # annual = annual.set_index("Date")  # <- enable if you prefer Date as index
        return annual

    else:
        raise ValueError("Invalid timestep. Use 'monthly' or 'annual'.")




def read_hru(filepath, timestep="monthly"):
    """
    Read SWAT2020 .hru output file using fixed-width format and
    return a DataFrame with a real Date column.
    
    Args:
        filepath (str): Path to the .hru file (e.g., 'C:/.../output_monthly.hru').
        timestep (str): 'monthly' or 'annual'.
    
    Returns:
        pd.DataFrame: DataFrame with parsed SWAT HRU output.
    """
    # Step 1: Read lines and find data start
    with open(filepath, "r") as f:
        lines = f.readlines()

    start_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("HRU") or line.strip().startswith("LULC"):
            start_line = i + 1
            break

    # Step 2: Column names and widths
    colnames = get_column_names()["hru"]
    widths = get_column_widths()["hru"]

    if len(colnames) != len(widths):
        raise ValueError("Mismatch between number of HRU column names and widths.")

    # Step 3: Read fixed-width data
    df = pd.read_fwf(filepath, skiprows=start_line, widths=widths, names=colnames)

    # Step 4: Parse dates
    n_hru = df["HRU"].nunique()
    n_rows = len(df)

    if timestep.lower() == "monthly":
        n_months = n_rows // n_hru

        # Detect start year from MON > 12 (annual summary rows)
        annual_rows = df[df["MON"] > 12]
        if not annual_rows.empty:
            start_year = int(annual_rows["MON"].min())
        else:
            raise ValueError("Could not detect start year from MON column.")

        # Generate dates in correct order
        dates = []
        year, month = start_year, 1
        for _ in range(n_months):
            dates.extend([datetime(year, month, 1)] * n_hru)
            month += 1
            if month > 12:
                month = 1
                year += 1

        if len(dates) != len(df):
            raise ValueError(f"Mismatch: {len(df)} rows vs {len(dates)} dates.")

        df["Date"] = pd.to_datetime(dates)

    elif timestep.lower() == "annual":
        annual_rows = df[df["MON"] > 12]
        if not annual_rows.empty:
            start_year = int(annual_rows["MON"].min())
        else:
            raise ValueError("Could not detect start year from MON column.")

        n_years = n_rows // n_hru
        years = list(range(start_year, start_year + n_years))
        dates = [datetime(y, 1, 1) for y in years for _ in range(n_hru)]
        df["Date"] = pd.to_datetime(dates)

    else:
        raise ValueError("Invalid timestep. Use 'monthly' or 'annual'.")

    return df
