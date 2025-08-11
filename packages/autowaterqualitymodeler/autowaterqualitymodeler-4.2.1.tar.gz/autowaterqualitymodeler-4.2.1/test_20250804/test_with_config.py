from autowaterqualitymodeler.utils.encryption import EncryptionManager
from autowaterqualitymodeler.core.config_manager import ConfigManager

# 使用配置管理器
config_manager = ConfigManager()
encryption_manager = EncryptionManager(config_manager)

file_path = "/mnt/d/OneDrive/OneDriveForBusiness/study/AutoWaterQualityModeler/test_20250804/encrypted_result_20250731_182159.bin"

print("配置管理器参数:")
print(f"Password: {encryption_manager.password}")
print(f"Salt: {encryption_manager.salt}")
print(f"IV: {encryption_manager.iv}")

# 读取文件查看IV
with open(file_path, 'rb') as f:
    file_data = f.read()
print(f"文件中的IV: {file_data[:16]}")

# 尝试解密
data = encryption_manager.decrypt_file(file_path)

if data:
    print("解密成功!")
    print(f"数据类型: {type(data)}")
    if isinstance(data, dict):
        print(f"数据键: {list(data.keys())}")
        # 只显示部分数据避免输出过多
        for key, value in list(data.items())[:3]:
            print(f"  {key}: {type(value)} ({'长度' + str(len(value)) if hasattr(value, '__len__') else str(value)[:50]})")
else:
    print("解密失败")