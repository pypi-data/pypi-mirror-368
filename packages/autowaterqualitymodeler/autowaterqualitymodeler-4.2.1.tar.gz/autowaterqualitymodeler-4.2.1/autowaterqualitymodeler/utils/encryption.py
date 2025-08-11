"""
加密工具模块，提供数据加密和解密功能
"""
import json
import os
import logging
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Any


class EncryptionManager:
    """加密管理器，使用配置文件管理加密参数"""
    
    def __init__(self, config_manager=None):
        """
        初始化加密管理器
        
        Args:
            config_manager: 配置管理器实例，如果为None则使用默认参数
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # 获取加密配置
        if config_manager:
            self.password = config_manager.get_system_config('system', 'encryption', 'password')
            self.salt = config_manager.get_system_config('system', 'encryption', 'salt')
            self.iv = config_manager.get_system_config('system', 'encryption', 'iv')
            self.iterations = config_manager.get_system_config('system', 'encryption', 'iterations') or 100000
            self.key_length = config_manager.get_system_config('system', 'encryption', 'key_length') or 32
        else:
            # 使用默认值
            self.password = "water_quality_analysis_key"
            self.salt = "water_quality_salt"
            self.iv = "fixed_iv_16bytes"
            self.iterations = 100000
            self.key_length = 32
            
        # 转换为字节
        self.password = self.password.encode('utf-8') if isinstance(self.password, str) else self.password
        self.salt = self.salt.encode('utf-8') if isinstance(self.salt, str) else self.salt
        self.iv = (self.iv.encode('utf-8') if isinstance(self.iv, str) else self.iv)[:16]  # 确保IV是16字节
    
    def encrypt_data(self, data_obj: Any, output_dir: str | None = None) -> str | None:
        """
        加密数据并保存到文件
        
        Args:
            data_obj: 要加密的数据对象(将被转换为JSON)
            output_dir: 输出文件路径，若为None则自动生成
            
        Returns:
            str: 输出文件的路径，失败返回None
        """
        try:
            # 生成加密密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.key_length,
                salt=self.salt,
                iterations=self.iterations,
            )
            key = kdf.derive(self.password)
            
            # 准备加密器
            cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv))
            encryptor = cipher.encryptor()
            
            # 将结果转换为JSON
            data_json = json.dumps(data_obj, ensure_ascii=False)
            
            # 对数据进行填充
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data_json.encode('utf-8')) + padder.finalize()
            
            # 加密数据
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # 将IV与加密数据一起存储（IV可以是公开的）
            final_data = self.iv + encrypted_data
            
            # 如果未提供输出路径，则生成带时间戳的文件名
            if output_dir is None:
                # 从配置获取默认目录
                if self.config_manager:
                    output_dir = self.config_manager.get_system_config('system', 'output', 'models_dir')
                if not output_dir:
                    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'models')
                os.makedirs(output_dir, exist_ok=True)
                
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"encrypted_result_{timestamp}.bin")
            
            # 保存加密数据到文件
            with open(output_path, 'wb') as f:
                f.write(final_data)
            
            self.logger.info(f"结果已加密并保存到: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"加密数据时出错: {str(e)}")
            return None
    
    def decrypt_file(self, file_path: str) -> dict | None:
        """
        解密文件内容
        
        Args:
            file_path: 加密文件路径
            
        Returns:
            dict: 解密后的JSON数据对象，失败时返回None
        """
        try:
            # 读取加密文件
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            # 从文件读取IV（前16字节）
            iv = file_data[:16]
            encrypted_data = file_data[16:]
            
            # 从密码和盐值生成密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.key_length,
                salt=self.salt,
                iterations=self.iterations,
            )
            key = kdf.derive(self.password)
            
            # 解密
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            
            # 解密数据
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # 移除填充
            unpadder = padding.PKCS7(128).unpadder()
            decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
            
            # 解析JSON
            result = json.loads(decrypted_data)
            self.logger.info(f"成功解密文件: {file_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"解密文件失败: {str(e)}")
            return None


# 保留旧的函数接口以保持向后兼容
def encrypt_data_to_file(data_obj, password=b"water_quality_analysis_key", 
                         salt=b"water_quality_salt", iv=b"fixed_iv_16bytes", 
                         output_dir=None, logger=None):
    """旧的加密函数接口，保持向后兼容"""
    # 创建临时的加密管理器
    manager = EncryptionManager()
    if logger:
        manager.logger = logger
    
    # 如果提供了自定义参数，更新管理器的参数
    if isinstance(password, bytes):
        manager.password = password
    if isinstance(salt, bytes):
        manager.salt = salt
    if isinstance(iv, bytes):
        manager.iv = iv[:16]
        
    return manager.encrypt_data(data_obj, output_dir)


def decrypt_file(file_path, password=b"water_quality_analysis_key", 
                salt=b"water_quality_salt", logger=None):
    """旧的解密函数接口，保持向后兼容"""
    # 创建临时的加密管理器
    manager = EncryptionManager()
    if logger:
        manager.logger = logger
        
    # 如果提供了自定义参数，更新管理器的参数
    if isinstance(password, bytes):
        manager.password = password
    if isinstance(salt, bytes):
        manager.salt = salt
        
    return manager.decrypt_file(file_path) 