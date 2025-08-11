from autowaterqualitymodeler.utils.encryption import EncryptionManager

file_path = "/mnt/d/OneDrive/OneDriveForBusiness/study/AutoWaterQualityModeler/test_20250804/encrypted_result_20250731_182159.bin"

# 读取文件中的IV
with open(file_path, 'rb') as f:
    file_data = f.read()

actual_iv = file_data[:16]
print(f"文件中的IV: {actual_iv}")

# 尝试几种可能的参数组合
param_combinations = [
    # 默认参数
    {"password": "water_quality_analysis_key", "salt": "water_quality_salt", "iv": "fixed_iv_16bytes"},
    # 可能使用了默认EncryptionManager
    {"password": "water_quality_analysis_key", "salt": "water_quality_salt", "iv": actual_iv},
]

for i, params in enumerate(param_combinations):
    print(f"\n尝试参数组合 {i+1}:")
    print(f"  password: {params['password']}")
    print(f"  salt: {params['salt']}")
    print(f"  iv: {params['iv']}")
    
    try:
        manager = EncryptionManager()
        manager.password = params['password'].encode('utf-8') if isinstance(params['password'], str) else params['password']
        manager.salt = params['salt'].encode('utf-8') if isinstance(params['salt'], str) else params['salt'] 
        
        # 不设置IV，让解密方法从文件中读取
        data = manager.decrypt_file(file_path)
        
        if data:
            print(f"  ✓ 解密成功!")
            print(f"  数据类型: {type(data)}")
            if hasattr(data, 'keys'):
                print(f"  数据键: {list(data.keys())}")
            break
        else:
            print(f"  ✗ 解密失败")
            
    except Exception as e:
        print(f"  ✗ 异常: {e}")

# 如果都失败了，尝试原始decrypt_file函数的所有可能组合
print("\n尝试原始decrypt_file函数:")
from autowaterqualitymodeler.utils.encryption import decrypt_file

try:
    data = decrypt_file(file_path)  # 使用默认参数
    if data:
        print("✓ 使用默认参数解密成功!")
        print(f"数据: {data}")
    else:
        print("✗ 默认参数解密失败")
except Exception as e:
    print(f"✗ 默认参数异常: {e}")