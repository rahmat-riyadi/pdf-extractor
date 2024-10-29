import pdfplumber
import re
import mysql.connector
from pathlib import Path

folder_path = Path('files')
all_files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix == '.pdf']

print(all_files)

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="test_db"
)
cursor = conn.cursor()

insert_query = """
        INSERT INTO survey_data (fullname, gender, age, address, rt, rw, province, city, district, village, tps)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
try:

    for file in all_files:

        with pdfplumber.open(file) as pdf:

            kecamatan_name = None  
            kecamatan_pattern = r"KECAMATAN\s*:\s*(\w+)"  

            kelurahan_name = None 
            kelurahan_pattern = r"DESA/KELURAHAN\s*:\s*(\w+)" 

            tps_name = None 
            tps_pattern = r"TPS\s*:\s*(\w+)" 

            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    kecamatan_match = re.search(kecamatan_pattern, text)
                    kelurahan_match = re.search(kelurahan_pattern, text)
                    tps_match = re.search(tps_pattern, text)
                    if kecamatan_match:
                        kecamatan_name = kecamatan_match.group(1)
                    if kelurahan_match:
                        kelurahan_name = kelurahan_match.group(1)
                    if tps_match:
                        tps_name = tps_match.group(1)

                print(f"Kecamatan : {kecamatan_name}, Kelurahan : {kelurahan_name}, TPS : {tps_name}")

                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row[2].isdigit() and row[1] != 'NAMA':
                            formatted_row = row
                            del formatted_row[0]
                            del formatted_row[6]
                            formatted_row[1] = 'Laki-Laki' if row[1] == 'L' else 'Perempuan'
                            formatted_row.extend(['SULAWESI SELATAN', 'JENEPONTO', kecamatan_name, kelurahan_name, tps_name])
                            cursor.execute(insert_query, formatted_row)
                            print("inserted : ", formatted_row)
    conn.commit()
                        
except:
    conn.rollback()
    print("error")
finally:
    cursor.close()
    conn.close()
    print("finish")