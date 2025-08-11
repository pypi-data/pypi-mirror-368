from autowaterqualitymodeler.utils.encryption import EncryptionManager

# 创建完全相同的加密管理器
manager = EncryptionManager()

# 手动设置与加密时相同的参数
manager.password = b"water_quality_analysis_key"
manager.salt = b"water_quality_salt"
manager.iv = b"fixed_iv_16bytes"[:16]  # 确保是16字节

print(f"Password: {manager.password}")
print(f"Salt: {manager.salt}")
print(f"IV: {manager.iv}")
print(f"IV length: {len(manager.iv)}")

file_path = "/mnt/d/OneDrive/OneDriveForBusiness/study/AutoWaterQualityModeler/test_20250804/encrypted_result_20250731_182159.bin"

try:
    # 读取文件内容
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    print(f"File size: {len(file_data)} bytes")
    print(f"First 16 bytes (IV from file): {file_data[:16]}")
    print(f"Expected IV: {manager.iv}")
    print(f"IV match: {file_data[:16] == manager.iv}")
    
    # 尝试解密
    data = manager.decrypt_file(file_path)
    if data:
        print("解密成功！")
        print(data)
    else:
        print("解密失败")
        
except Exception as e:
    print(f"Error: {e}")