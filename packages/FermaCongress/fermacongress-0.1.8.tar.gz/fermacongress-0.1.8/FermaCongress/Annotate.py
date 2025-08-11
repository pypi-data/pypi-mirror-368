import os
import json
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from io import StringIO, BytesIO

session = None

def supportlogin(env_path):
    global session
    
    login_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://support.ferma.ai/main/login"
    }
    
    load_dotenv(dotenv_path=env_path)
    session = requests.Session()
    session.get("https://support.ferma.ai/main/login")

    login_data = {
        "username": os.getenv("FERMA_USERNAME"),
        "password": os.getenv("FERMA_PASSWORD")
    }
    response = session.post("https://support.ferma.ai/main/validate", data=login_data, headers=login_headers)
    
    if response.status_code == 200:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Ferma Support Portal Login successful")
        return session
    else:
        raise Exception(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Login failed - Invalid credentials or server error")
    
def annotate(input_df, custom_needles_df=None, needles=[1, 1], entities=None, long_table=True, poll_interval=10, max_wait=300):
    global session
    
    cookies_dict = session.cookies.get_dict()
    cookie_header = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
    download_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://support.ferma.ai/annotation/progress-tracker",
        "Cookie": cookie_header
    }
    
    if session is None:
        raise Exception("Session not initialized. Call supportlogin() first.")
        
    if len(needles) != 2:
        raise ValueError("`needles` must be a list of two integers: [kb_status, nct_status]")


    kb_status, nct_status = needles
    ordered_needles = []
    if kb_status == 1:
        ordered_needles.append("kb")
    if nct_status == 1:
        ordered_needles.append("nct")

    if custom_needles_df is not None:
        ordered_needles.append("custom")
        
    if 'id' not in input_df.columns:
        raise ValueError("Error! Input DataFrame must contain `id` column")

    csv_buffer = StringIO()
    input_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    files = {
        "input_csv": ("input.csv", csv_buffer, "text/csv")
    }

    if custom_needles_df is not None:
        custom_csv_buffer = StringIO()
        custom_needles_df.to_csv(custom_csv_buffer, index=False)
        custom_csv_buffer.seek(0)
        files["custom_needles"] = ("custom_needles.csv", custom_csv_buffer, "text/csv")

    # Prepare form data
    form_data = {
        "ann_name": "Annt",
        "output_db": "annotations",
        "output_table_name": "Annt",
        "entities": json.dumps(entities) if entities else "",
        "needles": ordered_needles
    }

    resp = session.post("https://support.ferma.ai/annotation/csv-input", data=form_data, files=files)
    if resp.status_code != 200:
        raise Exception(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Failed to initiate annotation")

    soup = BeautifulSoup(resp.text, "html.parser")
    trans_id = soup.find("input", {"name": "trans_id"})["value"]
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Annotation started, Transaction ID: {trans_id}")

    tracker_url = f"https://support.ferma.ai/annotation/progress-tracker?trans_id={trans_id}"
    waited = 0

    while waited < max_wait:
        progress_html = session.get(tracker_url).text
        soup = BeautifulSoup(progress_html, "html.parser")

        try:
            def get_value(field):
                cell = soup.find("td", string=field)
                return cell.find_next_sibling("td").text.strip() if cell else None

            total = int(get_value("total") or 0)
            completed = int(get_value("completed") or 0)
            failed = int(get_value("failed") or 0)
            failure_details = get_value("failure_details")
            last_modified_at = get_value("last_modified_at")

            print(f"• {waited:03d}s -> Completed: {completed}/{total} | Failed: {failed} | Last Modified: {last_modified_at}")
            if failed > 0:
                print(f"  Failure Details: {failure_details}")

            if total > 0 and completed >= total:
                break
        except Exception as e:
            print("Error parsing progress:", e)

        time.sleep(poll_interval)
        waited += poll_interval

    # Download results
    download_format = "long_table_format" if long_table else "pivot_table_format"
    files = {"trans_id": (None, trans_id), "format_type": (None, download_format)}
    start_download = time.time()
    download_resp = session.post("https://support.ferma.ai/annotation/progress-tracker", files=files, headers=download_headers)
    end_download = time.time()
    
    if download_resp.headers.get("Content-Type", "").startswith("text/csv"):
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Annotation Completed (Download retrieved in {end_download - start_download:.2f} secs)")
        return pd.read_csv(BytesIO(download_resp.content), encoding='utf-8-sig')
    else:
        raise Exception(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Download failed or invalid format received")