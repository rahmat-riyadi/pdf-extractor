import pdfplumber
import re
from pathlib import Path
import pandas as pd

folder_path = Path('files')
all_files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix == '.pdf']

data = []

for index, file in enumerate(all_files):
    print(f"{file} ==========> {index+1}/{len(all_files)}")
    with pdfplumber.open(file) as pdf:

        kecamatan_name = None  
        kecamatan_pattern = r"KECAMATAN\s*:\s*(.+)"  

        kelurahan_name = None 
        kelurahan_pattern = r"DESA/KELURAHAN\s*:\s*(.+)" 

        tps_name = None 
        tps_pattern = r"TPS\s*:\s*(\w+)" 

        total_pattern = r"Jumlah Pemilih \(L\+P\):\s*(\w+)"
        man_pattern = r"Pemilih Laki-laki:\s*(\w+)"
        woman_pattern = r"Pemilih Perempuan:\s*(\w+)"


        for page in pdf.pages:
            # print(f"kecamatan: {kecamatan_name}, kelurahan: {kelurahan_name}, tps: {tps_name}")
            text = page.extract_text()

            if text:
                kecamatan_match = re.search(kecamatan_pattern, text)
                kelurahan_match = re.search(kelurahan_pattern, text)
                tps_match = re.search(tps_pattern, text)
                total_match = re.search(total_pattern, text)
                men_match = re.search(man_pattern, text)
                woman_match = re.search(woman_pattern, text)

                if kecamatan_match:
                    kecamatan_name = kecamatan_match.group(1)
                if kelurahan_match:
                    kelurahan_name = kelurahan_match.group(1)
                if tps_match:
                    tps_name = tps_match.group(1)

                if total_match:
                    total = int(total_match.group(1))
                if men_match:
                    men_total = int(men_match.group(1))
                if woman_match:
                    woman_total = int(woman_match.group(1))

                if kecamatan_name and total_match:
                    data.append({
                        'Kecamatan': kecamatan_name,
                        'Kelurahan': kelurahan_name,
                        'TPS': tps_name,
                        'Pemilih Laki-laki': men_total,
                        'Pemilih Perempuan': woman_total,
                        'Total': total,
                    })

                        



# print(data)

df = pd.DataFrame(data)

df.to_excel("data_pemilih.xlsx", index=False)