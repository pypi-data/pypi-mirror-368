from autowaterqualitymodeler.utils.encryption import EncryptionManager

# 创建加密管理器，使用与加密时相同的参数
manager = EncryptionManager()
manager.password = b"water_quality_analysis_key"
manager.salt = b"water_quality_salt"

file_path = "/mnt/d/OneDrive/OneDriveForBusiness/study/AutoWaterQualityModeler/test_20250804/encrypted_result_20250731_182159.bin"

# 使用decrypt_file方法，它会从文件中读取正确的IV
data = manager.decrypt_file(file_path)

if data:
    print("解密成功！")
    print(data)
else:
    print("解密失败")