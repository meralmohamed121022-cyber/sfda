import os
import sys
import json
import re
import time
import urllib.parse
import urllib3
import requests
from flask import Flask, render_template, request, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# تحديد مسار القوالب ليعمل محلياً وعلى Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
template_dir = os.path.join(parent_dir, 'templates') if os.path.exists(os.path.join(parent_dir, 'templates')) else os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

HEADER_API_KEY = "453299022fd70f9329bb0c2bf5fa6a75dea07dc6"
cached_token = None
token_expiry_time = 0

def get_token():
    global cached_token, token_expiry_time
    now = time.time()
    if cached_token and now < token_expiry_time:
        return cached_token

    url = "https://apis.sfda.gov.sa:9002/tameni/v3/api/tokens/GetAccess"
    headers = {
        "User-Agent": "Dart/3.0 (dart:io)",
        "HEADER_API_KEY": HEADER_API_KEY,
    }
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            data = r.json()
            cached_token = data.get("token")
            token_expiry_time = now + 1800
            return cached_token
    except Exception as e:
        print(f"Error fetching token: {e}")
    return None

def extract_gtin_from_code(code):
    c = str(code).strip()
    m = re.search(r'\(01\)(\d{14}|\d{13})', c)
    if m:
        return m.group(1).lstrip('0')
    if c.startswith('01') and len(c) >= 16:
        return c[2:16].lstrip('0')
    clean = re.sub(r'\D', '', c)
    return clean.lstrip('0') if clean else c

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/scan', methods=['GET', 'POST'])
def scan_endpoint():
    code = request.args.get('code') or (request.json.get('code') if request.is_json else None)
    if not code:
        return jsonify({"success": False, "error": "لم يتم إرسال الباركود"}), 400

    code = str(code).strip()
    gtin_clean = extract_gtin_from_code(code)

    result = {
        "success": True,
        "scanned_code": code,
        "gtin": gtin_clean,
        "price_source": "سيرفر الهيئة لايف (SFDA Live API)",
        "rsd_info": None,
        "drug_info": None
    }

    token = get_token()
    if not token:
        return jsonify({"success": False, "error": "تعذر الحصول على توكن الهيئة. قد يكون السيرفر محجوباً خارج السعودية."}), 500

    auth_headers = {
        "User-Agent": "Dart/3.0 (dart:io)",
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    reg_no = None

    # 1. نظام رصد (RSD)
    clean_nums = re.sub(r'\D', '', code)
    if len(clean_nums) in [12, 13, 14]:
        gtin14 = clean_nums.zfill(14)
        rsd_payload = f"01{gtin14}1726123110123452112345678"
    else:
        rsd_payload = code

    try:
        rsd_url = f"https://apis.sfda.gov.sa:9002/v2/rsd/Drugs/status?qrCode={urllib.parse.quote(rsd_payload)}"
        r_rsd = requests.get(rsd_url, headers=auth_headers, timeout=8, verify=False)
        if r_rsd.status_code == 200:
            rsd_json = r_rsd.json().get('data', {})
            reg_no = rsd_json.get("druG_REGISTRATION_NO")
            result["rsd_info"] = {
                "registration_no": reg_no,
                "expiry_date": rsd_json.get("productexpiredate"),
                "status": rsd_json.get("operatioN_TYPE") or "سليم ومصرح",
                "recalled": rsd_json.get("operatioN_TYPE") != "Not Recalled" if rsd_json.get("operatioN_TYPE") else False
            }
    except Exception as e:
        print(f"RSD Error: {e}")

    # 2. البحث برقم التسجيل في Solr لجلب السعر لايف
    if reg_no:
        solr_url = f"https://apis.sfda.gov.sa:9002/v1/Solr/Search?q=RegisterNumber%3A{urllib.parse.quote(str(reg_no))}"
        try:
            r_solr = requests.get(solr_url, headers=auth_headers, timeout=8, verify=False)
            if r_solr.status_code == 200:
                docs = r_solr.json().get('data', {}).get('response', {}).get('docs', [])
                if docs:
                    result["drug_info"] = docs[0]
        except Exception as e:
            print(f"Solr RegNo Error: {e}")

    # 3. إذا لم يرجع بالرقم، ابحث بالاسم أو الباركود
    if not result["drug_info"]:
        solr_url = f"https://apis.sfda.gov.sa:9002/v1/Solr/Search?q={urllib.parse.quote(code)}"
        try:
            r_solr = requests.get(solr_url, headers=auth_headers, timeout=8, verify=False)
            if r_solr.status_code == 200:
                docs = r_solr.json().get('data', {}).get('response', {}).get('docs', [])
                if docs:
                    result["drug_info"] = docs[0]
        except Exception as e:
            print(f"Solr Search Error: {e}")

    if not result.get("drug_info") and not result.get("rsd_info"):
        return jsonify({
            "success": False,
            "error": "لم يتم العثور على بيانات لهذا الباركود في نظام رصد أو قاعدة بيانات الهيئة.",
            "code": code
        }), 404

    return jsonify(result)

# Vercel handler
app_handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
