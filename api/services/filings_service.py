import os
import pandas as pd
import re
import shutil
from sec_edgar_downloader import Downloader

def extract_dates(file_path):
    filing_date = None
    reporting_date = None

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(5000)

        filing_match = re.search(r'FILED AS OF DATE:\s*(\d{8})', content)
        if filing_match:
            filing_date = filing_match.group(1)

        reporting_match = re.search(r'CONFORMED PERIOD OF REPORT:\s*(\d{8})', content)
        if reporting_match:
            reporting_date = reporting_match.group(1)

    return filing_date, reporting_date

def download_filings(ticker: str, interval: str = "quarterly"):
    ticker = ticker.upper()
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", ticker)
    os.makedirs(base_path, exist_ok=True)

    dl = Downloader("CompanyName", "email@example.com", base_path)

    filings_data = []

    if interval == "yearly":
        dl.get("10-K", ticker, after="2015-01-01")
        form_type = "10-K"
    else:
        dl.get("10-Q", ticker, after="2015-01-01")
        form_type = "10-Q"

    temp_form_folder = os.path.join(base_path, "sec-edgar-filings", ticker, form_type)
    final_form_folder = os.path.join(base_path, form_type)

    if os.path.exists(temp_form_folder):
        if os.path.exists(final_form_folder):
            shutil.rmtree(final_form_folder)
        shutil.move(temp_form_folder, final_form_folder)

        for filing_dir in os.listdir(final_form_folder):
            filing_path = os.path.join(final_form_folder, filing_dir)
            if os.path.isdir(filing_path):
                full_submission = os.path.join(filing_path, "full-submission.txt")
                if os.path.exists(full_submission):
                    filing_date, reporting_date = extract_dates(full_submission)

                    filings_data.append({
                        "form_type": form_type,
                        "form_file": full_submission,
                        "filing_date": filing_date or "",
                        "reporting_date": reporting_date or ""
                    })

    sec_edgar_path = os.path.join(base_path, "sec-edgar-filings")
    if os.path.exists(sec_edgar_path):
        shutil.rmtree(sec_edgar_path)

    df = pd.DataFrame(filings_data)
    csv_path = os.path.join(base_path, "data.csv")
    df.to_csv(csv_path, index=False)

    return {"ticker": ticker, "interval": interval, "filings_count": len(filings_data), "saved_to": csv_path}
