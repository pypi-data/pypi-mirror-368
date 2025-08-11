import os

import numpy as np
import pandas as pd

from autowaterqualitymodeler.utils.encryption import decrypt_file

# 自动检测运行环境并使用正确的路径
if os.name == "nt":  # Windows
    file_path = r"D:\OneDrive\OneDriveForBusiness\study\AutoWaterQualityModeler\test_20250804\encrypted_result_20250806_101916.bin"
else:  # Linux/WSL
    file_path = "/mnt/d/OneDrive/OneDriveForBusiness/study/AutoWaterQualityModeler/test_20250804/encrypted_result_20250806_101916.bin"

data = decrypt_file(
    file_path, password=b"water_quality_analysis_key", salt=b"water_quality_salt"
)

# print(data)

w = np.array(data["Range"])
print(w.reshape(11, 2))
pd.DataFrame(w.reshape(11, 2)).to_csv("Range.csv")

