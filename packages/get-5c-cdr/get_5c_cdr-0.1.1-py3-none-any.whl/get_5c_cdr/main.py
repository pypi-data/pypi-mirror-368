import argparse
import datetime
from time import sleep

import os
import browsercookie
import pandas as pd
import requests
import subprocess


def search_telco(mobile_no, session_id):
    url = "https://ccib.cyberpolice.go.th/web/dataset/call_kw/tj_ccib_5c.telco_request/web_search_read"
    cookies = {"cids": "1", "frontend_lang": "th_TH", "tz": "Asia/Bangkok", "session_id": session_id}
    payload = {
        "id": 73,
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "tj_ccib_5c.telco_request",
            "method": "web_search_read",
            "args": [],
            "kwargs": {
                "domain": [["mobile_no", "ilike", mobile_no]],
                # "fields": ["mobile_no", "state"],
            },
        },
    }

    response = requests.post(url, cookies=cookies, json=payload)
    if response.ok:
        return response.json()


def get_mobile_number_and_id(input_file, column_name, session_id):
    results = []
    df = pd.read_excel(input_file)
    if column_name not in df.columns:
        return []

    numbers = df[column_name].dropna().astype(str).unique()
    for num in numbers[:1]:
        print(f"Searching for: {num}")
        data = search_telco(num, session_id)

        data = data.get("result", {"length": 0, "records": []})
        if len(data["records"]) > 0:
            received_result = [record for record in data["records"] if record.get("nbtc_status_code", 500) == 200]
            results.append({"mobile_no": num, "id": received_result[0].get("id", "") if received_result else "", "data": received_result[0] if received_result else {}})
    return results


def download_with_curl(output_path, mobile_id, session_id):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    curl_cmd = f"""
curl --progress-bar 'https://ccib.cyberpolice.go.th/report/download' \
  -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryZ3ZnRlc294uzHsZx' \
  -b 'cids=1; frontend_lang=th_TH; tz=Asia/Bangkok; session_id={session_id}' \
  -H 'Origin: https://ccib.cyberpolice.go.th' \
  -H 'Referer: https://ccib.cyberpolice.go.th/web' \
  --data-raw $'------WebKitFormBoundaryZ3ZnRlc294uzHsZx\\r\\nContent-Disposition: form-data; name="data"\\r\\n\\r\\n["/report/pdf/tj_ccib_smartdoc.number_audit_form/{mobile_id}","qweb-pdf"]\\r\\n------WebKitFormBoundaryZ3ZnRlc294uzHsZx\\r\\nContent-Disposition: form-data; name="context"\\r\\n\\r\\n{{"lang":"en_US","tz":"Asia/Bangkok","uid":4539,"allowed_company_ids":[1]}}\\r\\n------WebKitFormBoundaryZ3ZnRlc294uzHsZx\\r\\nContent-Disposition: form-data; name="token"\\r\\n\\r\\ndummy-because-api-expects-one\\r\\n------WebKitFormBoundaryZ3ZnRlc294uzHsZx\\r\\nContent-Disposition: form-data; name="csrf_token"\\r\\n\\r\\ne7f8befc3d24c387994e2aceb742faf87c0a90fco1786523572\\r\\n------WebKitFormBoundaryZ3ZnRlc294uzHsZx--\\r\\n' \
  --output "{output_path}"
"""
    subprocess.run(curl_cmd, shell=True, check=True)


def check_session():
    url = "https://ccib.cyberpolice.go.th/web"
    cli_cookies = browsercookie.chrome()
    response = requests.get(url, cookies=cli_cookies)

    cookie_header = response.headers.get("Set-Cookie", "")
    session_id = cookie_header.split("session_id=")[-1].split(";")[0]
    return session_id


def main():
    session_id = check_session()
    if not session_id:
        print("กรุณาเข้าสู่ระบบที่ https://ccib.cyberpolice.go.th/web/session/login")
        return

    parser = argparse.ArgumentParser(description="Search telco requests from Excel mobile numbers")
    parser.add_argument("-i", "--input_file", required=True, help="ไฟล์ Excel จาก Telco x ข้อมูลเคส")
    parser.add_argument("-c", "--column_name", default="โทรฯ คนร้าย", help="ชื่อคอลัมน์ที่มีหมายเลขโทรศัพท์ (โทรฯ คนร้าย)")
    args = parser.parse_args()

    register_name = args.input_file.split("-")[-1].split(".")[0].strip()
    mobile_list = get_mobile_number_and_id(args.input_file, args.column_name, session_id)
    for item in mobile_list:
        if item["id"]:
            download_with_curl(f"ข้อมูลบุคคลจดทะเบียนโดย {register_name}/0{item['mobile_no']}.pdf", item["id"], session_id)
            # sleep(1)


if __name__ == "__main__":
    main()
