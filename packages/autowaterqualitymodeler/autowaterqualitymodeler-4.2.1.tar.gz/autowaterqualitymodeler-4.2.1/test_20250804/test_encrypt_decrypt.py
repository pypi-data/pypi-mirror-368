from autowaterqualitymodeler.utils.encryption import encrypt_data_to_file, decrypt_file

# 测试数据
test_data = {"test": "data", "numbers": [1, 2, 3]}

# 使用相同的参数加密
encrypted_path = encrypt_data_to_file(
    data_obj=test_data,
    password=b"water_quality_analysis_key",
    salt=b"water_quality_salt", 
    iv=b"fixed_iv_16bytes",
    output_dir="/mnt/d/OneDrive/OneDriveForBusiness/study/AutoWaterQualityModeler/test_20250804/"
)

print(f"加密文件路径: {encrypted_path}")

if encrypted_path:
    # 解密
    decrypted_data = decrypt_file(
        encrypted_path,
        password=b"water_quality_analysis_key",
        salt=b"water_quality_salt"
    )
    
    if decrypted_data:
        print("测试解密成功!")
        print(f"原始数据: {test_data}")
        print(f"解密数据: {decrypted_data}")
        print(f"数据一致: {test_data == decrypted_data}")
    else:
        print("测试解密失败")
        
    # 检查新文件的IV
    with open(encrypted_path, 'rb') as f:
        file_data = f.read()
    print(f"新文件的IV: {file_data[:16]}")
    print(f"预期IV: {b'fixed_iv_16bytes'}")
else:
    print("加密失败")