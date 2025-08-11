import os
import json
from urllib.parse import urlparse
import requests

TARIFF_DATA_FILE = "https://raw.githubusercontent.com/nbrshamim/bdtariff/refs/heads/main/Tariff.json"

class TariffSearch:
    def __init__(self, data):
        if isinstance(data, str):
            self.json_filepath = data
            self.data = self._load_data()
        else:
            self.json_filepath = None
            self.data = data
            
        self.hscode_map = self._build_hscode_map()

    def _load_data(self):
        if not os.path.exists(self.json_filepath):
            raise FileNotFoundError(f"JSON file not found at: {self.json_filepath}")
        
        try:
            with open(self.json_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                flattened_data = []
                for key, value in data.items():
                    if isinstance(value, list):
                        flattened_data.extend(value)
                    elif isinstance(value, dict):
                        flattened_data.append(value)
                data = flattened_data
                
            if not isinstance(data, list):
                raise ValueError("JSON data must be a list of records or a dictionary containing lists of records.")

            for record in data:
                if 'Hscode' in record and not isinstance(record['Hscode'], str):
                    record['Hscode'] = str(record['Hscode'])
            
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.json_filepath}: {e}")
        except Exception as e:
            raise Exception(f"Error loading JSON data: {e}")

    def _build_hscode_map(self):
        hscode_map = {}
        for record in self.data:
            if 'Hscode' in record and record['Hscode'] is not None:
                hscode_map[record['Hscode']] = record
        return hscode_map

    def search_by_hscode(self, hscode):
        if not isinstance(hscode, str):
            hscode = str(hscode)
        return self.hscode_map.get(hscode)

    def get_all_hscodes(self):
        return list(self.hscode_map.keys())

    def get_all_data(self):
        return self.data
        
def is_url(path):
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

class HscodeResult:
    def __init__(self, data):
        self._data = data or {}

    def __getattr__(self, item):
        for key in self._data:
            if key.lower() == item.lower():
                return self._data[key]
        raise AttributeError(f"'HscodeResult' object has no attribute '{item}'")

    def __getitem__(self, item):
        return self._data[item]

    def as_dict(self):
        return self._data

_tariff_db = None

def _initialize_tariff_db():
    global _tariff_db
    if _tariff_db is None:
        if is_url(TARIFF_DATA_FILE):
            response = requests.get(TARIFF_DATA_FILE)
            response.raise_for_status()
            tariff_data = response.json()
            _tariff_db = TariffSearch(tariff_data)
        else:
            _tariff_db = TariffSearch(TARIFF_DATA_FILE)

def hscode(hscode_value):
    _initialize_tariff_db()
    result = _tariff_db.search_by_hscode(hscode_value)
    if result:
        return HscodeResult(result)
    return None

def rate():
    _initialize_tariff_db()
    while True:
        hscode_input = input("\nEnter HSCode to search (or 'q' to quit): ").strip()
        if hscode_input.lower() == 'q':
            break

        if not hscode_input:
            print("Please enter a valid HSCode.")
            continue

        result = hscode(hscode_input)

        if result:
            print(f"\n--- Tariff Information for HSCode: {hscode_input} ---")
            print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
            print("------------------------------------------")
        else:
            print(f"No tariff information found for HSCode: {hscode_input}")
            
def duty():
    hscode_data = hscode(input("Enter HSCode: "))
    av = eval(input("Enter Assess Value in BDT: "))
    if hscode_data:
        print(hscode_data)
        if hscode_data.TTI == '':
            cd = hscode_data.CD
            rd = (av*(hscode_data.RD/100))
            sd = ((av+cd+rd)*(hscode_data.SD/100))
            vat = ((av+cd+rd+sd)*(hscode_data.VAT/100))
            at = ((av+cd+rd+sd)*(hscode_data.AT/100))
            ait = (av*(hscode_data.AIT/100))
            tti = cd+rd+sd+vat+at+ait
            print('----- Duty Information for HSCode: -----')
            print(f"HSCode Description: {hscode_data.TARRIFF_DESCRIPTION}")
            print(f"CD (rate: {hscode_data.CD}): {round(cd,2)}")
            print(f"RD (rate: {hscode_data.RD}): {round(rd,2)}")
            print(f"SD (rate: {hscode_data.SD}): {round(sd,2)}")
            print(f"VAT (rate: {hscode_data.VAT}): {round(vat,2)}")
            print(f"AT (rate: {hscode_data.AT}): {round(at,2)}")
            print(f"AIT (rate: {hscode_data.AIT}): {round(ait,2)}")
            print('----------------------------------------------')
            print(f"Total Duty in BDT: {round(tti,2)}")    
        else:
            cd = (av*(hscode_data.CD/100))
            rd = (av*(hscode_data.RD/100))
            sd = ((av+cd+rd)*(hscode_data.SD/100))
            vat = ((av+cd+rd+sd)*(hscode_data.VAT/100))
            at = ((av+cd+rd+sd)*(hscode_data.AT/100))
            ait = (av*(hscode_data.AIT/100))
            tti = cd+rd+sd+vat+at+ait
            print('----- Duty Information for HSCode: -----')
            print(f"HSCode Description: {hscode_data.TARRIFF_DESCRIPTION}")
            print(f"CD (rate: {hscode_data.CD}): {round(cd,2)}")
            print(f"RD (rate: {hscode_data.RD}): {round(rd,2)}")
            print(f"SD (rate: {hscode_data.SD}): {round(sd,2)}")
            print(f"VAT (rate: {hscode_data.VAT}): {round(vat,2)}")
            print(f"AT (rate: {hscode_data.AT}): {round(at,2)}")
            print(f"AIT (rate: {hscode_data.AIT}): {round(ait,2)}")
            print('----------------------------------------------')
            print(f"Total Duty in BDT: {round(tti,2)}")
    else:
        print("HSCode not found.")
        
def duty(hsc,av):
    hscode_data = hscode(hsc)
    av = av
    if hscode_data:
        print(hscode_data)
        if hscode_data.TTI == '':
            code = hscode_data.hscode
            description = hscode_data.TARRIFF_DESCRIPTION
            cd = round(hscode_data.CD,2)
            rd = round((av*(hscode_data.RD/100)),2)
            sd = round(((av+cd+rd)*(hscode_data.SD/100)),2)
            vat = round(((av+cd+rd+sd)*(hscode_data.VAT/100)),2)
            at = round(((av+cd+rd+sd)*(hscode_data.AT/100)),2)
            ait = round((av*(hscode_data.AIT/100)),2)
            tti = round((cd+rd+sd+vat+at+ait),2)
            return code,description,cd,rd,sd,vat,at,ait,tti  
        else:
            code = hscode_data.hscode
            description = hscode_data.TARRIFF_DESCRIPTION
            cd = round((av*(hscode_data.CD/100)),2)
            rd = round((av*(hscode_data.RD/100)),2)
            sd = round(((av+cd+rd)*(hscode_data.SD/100)),2)
            vat = round(((av+cd+rd+sd)*(hscode_data.VAT/100)),2)
            at = round(((av+cd+rd+sd)*(hscode_data.AT/100)),2)
            ait = round((av*(hscode_data.AIT/100)),2)
            tti = round((cd+rd+sd+vat+at+ait),2)
            return code,description,cd,rd,sd,vat,at,ait,tti
    else:
        print("HSCode not found.")

if __name__ == "__main__":
    rate()