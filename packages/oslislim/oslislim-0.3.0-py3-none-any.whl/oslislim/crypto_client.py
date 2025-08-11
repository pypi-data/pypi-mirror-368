#!/usr/bin/env python3
"""
OSLisLim 加密客户端
用于在用户项目中解密和执行受保护的代码
"""

import os
import sys
import json
import hashlib
import random
import string
import base64
import inspect
import marshal
import types
import platform
import time
import threading
from typing import Dict, Any, Callable
from datetime import datetime


class OSLisLimDecryptor:
    """OSLisLim 解密器 - 与服务端加密引擎对应"""
    
    def __init__(self):
        self.master_key = "OSLisLim_2025_Protection_Key_Advanced"
        self.salt_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        self.char_map = self._generate_char_map()
        self.reverse_char_map = {v: k for k, v in self.char_map.items()}
    
    def _generate_char_map(self) -> Dict[str, str]:
        """生成与服务端相同的字符映射表"""
        base_chars = string.ascii_letters + string.digits + string.punctuation + " \n\t"
        mapped_chars = []
        for i, char in enumerate(base_chars):
            unicode_offset = 0xE000 + (i * 7) % 0x1000
            mapped_chars.append(chr(unicode_offset))
        return dict(zip(base_chars, mapped_chars))
    
    def _custom_hash(self, data: str) -> str:
        """与服务端相同的自定义哈希函数"""
        result = data
        for i in range(3):
            result = hashlib.sha256((result + self.master_key + str(i)).encode()).hexdigest()
        return result
    
    def _xor_encrypt(self, data: str, key: str) -> str:
        """XOR 加密/解密（对称）"""
        result = []
        key_len = len(key)
        for i, char in enumerate(data):
            key_char = key[i % key_len]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            result.append(encrypted_char)
        return ''.join(result)
    
    def _char_substitute(self, data: str, encrypt: bool = True) -> str:
        """字符替换"""
        char_map = self.char_map if encrypt else self.reverse_char_map
        result = []
        for char in data:
            mapped_char = char_map.get(char, char)
            result.append(mapped_char)
        return ''.join(result)
    
    def _position_unscramble(self, data: str, salt: str) -> str:
        """位置还原"""
        if len(data) <= 1:
            return data
        
        random.seed(self._custom_hash(salt))
        indices = list(range(len(data)))
        random.shuffle(indices)
        
        unscrambled = [''] * len(data)
        for i, original_pos in enumerate(indices):
            unscrambled[original_pos] = data[i]
        
        return ''.join(unscrambled)
    
    def _decode_from_printable(self, data: str) -> str:
        """从可打印字符解码"""
        char_replacements = {
            'Ω': 'A', 'Ψ': 'B', 'Φ': 'C', 'Υ': 'D', 'Τ': 'E',
            'ω': 'a', 'ψ': 'b', 'φ': 'c', 'υ': 'd', 'τ': 'e',
            '§': '+', '¶': '/', '∞': '='
        }
        
        result = data
        for old, new in char_replacements.items():
            result = result.replace(old, new)
        
        data_bytes = base64.b64decode(result.encode('ascii'))
        return data_bytes.decode('utf-8')
    
    def decrypt_payload(self, encrypted_data: str) -> Dict[str, Any]:
        """解密数据载荷"""
        try:
            # 分离盐值和加密数据
            salt, encoded_data = encrypted_data.split(':', 1)
            
            # 解码
            decoded_data = self._decode_from_printable(encoded_data)
            
            # 多层解密
            # 第3层：位置还原
            layer3 = self._position_unscramble(decoded_data, salt)
            
            # 第2层：XOR 解密
            xor_key = self._custom_hash(salt + self.master_key)[:32]
            layer2 = self._xor_encrypt(layer3, xor_key)
            
            # 第1层：字符替换还原
            layer1 = self._char_substitute(layer2, encrypt=False)
            
            # 解析 JSON
            payload = json.loads(layer1)
            return payload
            
        except Exception as e:
            raise RuntimeError(f"解密失败，可能是包被篡改或损坏: {e}")


# 全局解密器实例
_decryptor = OSLisLimDecryptor()
_active_tracker = None
_active_config = None

# 反调试和安全检测
def _detect_debugging_environment():
    """检测调试和逆向环境"""
    try:
        # 检测调试器
        if hasattr(sys, 'gettrace') and sys.gettrace():
            raise RuntimeError("Debugging environment detected")

        # 检测逆向工具模块（只检测明显的逆向工具）
        suspicious_modules = [
            'uncompyle6', 'decompyle3', 'unpyc37', 'pycdc',
            'pdb', 'trace', 'bdb'
        ]

        loaded_suspicious = [m for m in suspicious_modules if m in sys.modules]
        if loaded_suspicious:
            raise RuntimeError(f"Reverse engineering tools detected: {loaded_suspicious}")

        # 检测虚拟机环境
        vm_indicators = [
            'vmware', 'virtualbox', 'qemu', 'xen', 'parallels'
        ]

        system_info = platform.platform().lower()
        for indicator in vm_indicators:
            if indicator in system_info:
                # 在虚拟机中运行，增加额外检查
                pass

        # 检测分析工具进程（Windows）
        if platform.system() == "Windows":
            try:
                import subprocess
                result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    processes = result.stdout.lower()
                    analysis_tools = ['ollydbg', 'x64dbg', 'ida', 'ghidra', 'radare2']
                    for tool in analysis_tools:
                        if tool in processes:
                            raise RuntimeError(f"Analysis tool detected: {tool}")
            except:
                pass

    except Exception as e:
        if "detected" in str(e).lower():
            raise e

# 动态密钥生成
def _generate_dynamic_master_key():
    """基于环境特征生成动态主密钥"""
    try:
        # 收集环境特征
        factors = [
            platform.python_version()[:3],  # Python 版本
            platform.system(),              # 操作系统
            str(hash("OSLisLim_2025")),     # 固定哈希
            str(os.getpid() % 1000),        # 进程ID（取模）
        ]

        # 添加时间因子（小时级别，避免频繁变化）
        time_factor = str(int(time.time() // 3600) % 100)
        factors.append(time_factor)

        # 生成主密钥
        combined = ''.join(factors)
        master_key = hashlib.sha256(combined.encode()).hexdigest()

        # 进一步混淆
        obfuscated_key = ""
        for i, char in enumerate(master_key):
            obfuscated_key += chr((ord(char) ^ (i % 256)) % 256 + 32)

        return base64.b64encode(obfuscated_key.encode()).decode()[:32]

    except Exception:
        # 降级到固定密钥
        return "OSLisLim_Fallback_Key_2025_Secure"

# 字符串混淆
def _obfuscate_string(s):
    """混淆字符串"""
    try:
        encoded = base64.b64encode(s.encode()).decode()
        return ''.join(chr(ord(c) ^ 42) for c in encoded)
    except:
        return s

def _deobfuscate_string(s):
    """反混淆字符串"""
    try:
        decoded = ''.join(chr(ord(c) ^ 42) for c in s)
        return base64.b64decode(decoded.encode()).decode()
    except:
        return s

# 混淆后的配置
_OBFUSCATED_PREFIX = _obfuscate_string("OSL_")
_DYNAMIC_MASTER_KEY = None

def _get_master_key():
    """获取主密钥（延迟生成）"""
    global _DYNAMIC_MASTER_KEY
    if _DYNAMIC_MASTER_KEY is None:
        _detect_debugging_environment()  # 安全检查
        _DYNAMIC_MASTER_KEY = _generate_dynamic_master_key()
    return _DYNAMIC_MASTER_KEY

def _get_data_prefix():
    """获取数据前缀"""
    return _deobfuscate_string(_OBFUSCATED_PREFIX)

# 混淆的环境检查
def _advanced_environment_check():
    """高级环境检查"""
    try:
        # 检查执行时间（防止静态分析）
        start_time = time.time()

        # 执行一些计算来消耗时间
        dummy_calc = sum(i * i for i in range(1000))

        elapsed = time.time() - start_time
        if elapsed < 0.001:  # 如果执行太快，可能是在模拟器中
            pass  # 可以添加额外检查

        # 检查内存使用情况
        try:
            import psutil
            memory_info = psutil.virtual_memory()
            if memory_info.total < 1024 * 1024 * 1024:  # 小于 1GB
                pass  # 可能是受限环境
        except ImportError:
            pass

        # 检查文件系统
        temp_file = f"temp_check_{random.randint(1000, 9999)}.tmp"
        try:
            with open(temp_file, 'w') as f:
                f.write("test")
            os.remove(temp_file)
        except:
            pass  # 文件系统受限

        # 检查网络连接（可选）
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('8.8.8.8', 53))
            sock.close()
            if result != 0:
                pass  # 网络受限
        except:
            pass

        return True

    except Exception:
        return True

# 动态代码生成器
def _generate_obfuscated_code(template: str, variables: dict) -> str:
    """生成混淆的代码"""
    try:
        _detect_debugging_environment()
        _advanced_environment_check()

        # 变量名混淆
        var_map = {}
        for var in variables:
            obfuscated_name = ''.join(random.choices(string.ascii_letters, k=8))
            var_map[var] = obfuscated_name

        # 替换变量名
        obfuscated_template = template
        for original, obfuscated in var_map.items():
            obfuscated_template = obfuscated_template.replace(f"{{{original}}}", obfuscated)

        # 添加变量定义
        var_definitions = []
        for original, obfuscated in var_map.items():
            if original in variables:
                var_definitions.append(f"{obfuscated} = {repr(variables[original])}")

        final_code = '\n'.join(var_definitions) + '\n' + obfuscated_template

        return final_code

    except Exception:
        return template.format(**variables)


def detect_packaging_environment():
    """检测是否在打包环境中运行"""
    packaging_indicators = [
        # PyInstaller 检测
        hasattr(sys, 'frozen'),
        hasattr(sys, '_MEIPASS'),
        '_MEIPASS' in os.environ,

        # cx_Freeze 检测
        hasattr(sys, 'frozen') and hasattr(sys, 'frozen'),

        # Nuitka 检测
        '__compiled__' in globals(),

        # 可执行文件检测
        sys.executable.endswith('.exe') and 'python' not in sys.executable.lower(),

        # 临时目录检测
        any(temp_dir in sys.executable.lower() for temp_dir in ['temp', 'tmp', '_mei']),

        # 检查是否能找到当前 Python 文件
        not _verify_source_environment()
    ]

    return any(packaging_indicators)


def _verify_source_environment():
    """验证是否在源代码环境中运行"""
    try:
        # 获取调用栈
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_code.co_filename
            # 检查是否有 .py 文件存在
            if filename.endswith('.py') and os.path.exists(filename):
                return True
            frame = frame.f_back
        return False
    except Exception:
        return False


def get_environment_info():
    """获取环境信息用于调试"""
    return {
        "sys.frozen": hasattr(sys, 'frozen'),
        "sys._MEIPASS": hasattr(sys, '_MEIPASS'),
        "sys.executable": sys.executable,
        "python_in_executable": 'python' in sys.executable.lower(),
        "executable_extension": os.path.splitext(sys.executable)[1],
        "current_file_exists": _verify_source_environment(),
        "environment_vars": {k: v for k, v in os.environ.items() if 'mei' in k.lower() or 'temp' in k.lower()}
    }


def decrypt_and_execute_bundle(encrypted_data: str) -> Dict[str, Any]:
    """解密并执行加密包"""
    global _active_tracker, _active_config

    # 首先检测打包环境
    if detect_packaging_environment():
        env_info = get_environment_info()
        error_msg = f"""
🚫 检测到打包环境，拒绝运行！

OSLisLim 保护机制：此开源项目不允许在打包后的可执行文件中运行。
这是为了防止商业滥用和未经授权的分发。

检测到的环境特征：
- 可执行文件: {env_info['sys.executable']}
- 是否打包: {env_info['sys.frozen']}
- 源文件存在: {env_info['current_file_exists']}

如果您是合法用户，请：
1. 使用源代码方式运行：python your_script.py
2. 确保 Python 环境正确安装
3. 联系项目作者获取商业授权

如果您是项目作者，可以在配置中添加白名单。
        """
        raise RuntimeError(error_msg.strip())

    try:
        # 解密数据
        payload = _decryptor.decrypt_payload(encrypted_data)

        # 提取配置和代码
        config = payload.get('config', {})
        tracker_code = payload.get('tracker_code', '')
        core_functions = payload.get('core_functions', [])

        # 验证必要字段
        if not config.get('project_name'):
            raise RuntimeError("无效的保护包：缺少项目名称")

        # 执行追踪器代码
        if tracker_code:
            try:
                # 创建执行环境
                exec_globals = {
                    '__builtins__': __builtins__,
                    'os': __import__('os'),
                    'json': __import__('json'),
                    'datetime': __import__('datetime'),
                    'time': __import__('time')
                }

                # 执行追踪器代码
                exec(tracker_code, exec_globals)

                # 查找追踪器函数
                for name, obj in exec_globals.items():
                    if callable(obj) and name.endswith('_tracker'):
                        _active_tracker = obj
                        break

            except Exception as e:
                print(f"⚠️ 追踪器初始化失败: {e}")

        # 保存配置
        _active_config = config

        # 返回解密结果
        return {
            "success": True,
            "config": config,
            "tracker_loaded": _active_tracker is not None,
            "core_functions": core_functions
        }

    except Exception as e:
        raise RuntimeError(f"保护包加载失败: {e}")


def decrypt_and_execute(bundle_file: str) -> Dict[str, Any]:
    """从文件解密并执行加密包"""
    try:
        with open(bundle_file, 'r', encoding='utf-8') as f:
            bundle_content = f.read().strip()

        # 新格式：整行都是加密的
        if bundle_content.startswith("exec("):
            # 创建执行环境，包含当前模块的全局变量
            exec_globals = globals().copy()
            exec_globals.update({
                '__builtins__': __builtins__,
                'json': __import__('json'),
                'base64': __import__('base64'),
                'hashlib': __import__('hashlib'),
                'random': __import__('random'),
                'string': __import__('string'),
                'oslislim': __import__('oslislim')
            })

            # 执行加密的代码
            exec(bundle_content, exec_globals)

            # 检查是否成功初始化（从执行环境中获取）
            # 寻找混淆后的变量名
            config_found = False
            tracker_found = False

            for var_name, var_value in exec_globals.items():
                # 检查配置变量（字典类型且包含项目信息）
                if isinstance(var_value, dict) and 'project_name' in str(var_value):
                    global _active_config
                    _active_config = var_value
                    config_found = True
                # 检查追踪器变量（函数类型）
                elif callable(var_value) and 'tracker' in var_name.lower():
                    global _active_tracker
                    _active_tracker = var_value
                    tracker_found = True

            # 也检查旧的变量名（向后兼容）
            if not config_found and exec_globals.get('_active_config'):
                _active_config = exec_globals.get('_active_config')
                config_found = True

            if not tracker_found and exec_globals.get('_active_tracker'):
                _active_tracker = exec_globals.get('_active_tracker')
                tracker_found = True

            # 简化检测：只要代码执行成功就认为初始化成功
            # 确保设置全局变量
            if not config_found:
                _active_config = {"project_name": "Protected Project"}

            return {
                "success": True,
                "config": _active_config,
                "tracker_loaded": tracker_found
            }

        # 兼容旧格式
        lines = bundle_content.split('\n')
        for line in lines:
            if 'self._data = "' in line:
                start = line.find('"') + 1
                end = line.rfind('"')
                encrypted_data = line[start:end]
                return decrypt_and_execute_bundle(encrypted_data)

        raise RuntimeError("无法从包文件中提取加密数据")

    except FileNotFoundError:
        raise RuntimeError(f"保护包文件不存在: {bundle_file}")
    except Exception as e:
        raise RuntimeError(f"保护包文件读取失败: {e}")


def protect_function(func: Callable) -> Callable:
    """保护函数装饰器"""
    def wrapper(*args, **kwargs):
        # 检查是否已加载保护
        if not _active_config:
            raise RuntimeError("保护机制未初始化，请先调用 decrypt_and_execute")
        
        # 调用追踪器
        if _active_tracker:
            try:
                _active_tracker(func.__name__, args, kwargs)
            except Exception:
                pass  # 追踪器错误不应影响主功能
        
        # 执行原函数
        return func(*args, **kwargs)
    
    return wrapper


def require_protection(bundle_file: str):
    """要求保护装饰器 - 用于保护整个模块"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 自动加载保护
            if not _active_config:
                try:
                    decrypt_and_execute(bundle_file)
                except Exception as e:
                    raise RuntimeError(f"无法加载保护机制: {e}")
            
            # 应用函数保护
            protected_func = protect_function(func)
            return protected_func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_protection_status() -> Dict[str, Any]:
    """获取保护状态"""
    return {
        "protected": _active_config is not None,
        "project_name": _active_config.get('project_name') if _active_config else None,
        "author": _active_config.get('author') if _active_config else None,
        "tracker_active": _active_tracker is not None,
        "protection_level": _active_config.get('protection_level') if _active_config else None
    }


# 混淆的加密函数
def _obfuscated_encrypt_function():
    """动态生成加密函数"""
    _detect_debugging_environment()

    # 使用 marshal 和 exec 动态创建函数
    func_code = '''
def _advanced_xor_encrypt(data, key):
    """高级 XOR 加密"""
    result = []
    key_hash = hash(key) % 256

    for i, char in enumerate(data):
        # 多层异或
        key_char = key[i % len(key)]
        layer1 = ord(char) ^ ord(key_char)
        layer2 = layer1 ^ (i % 256)
        layer3 = layer2 ^ key_hash
        layer4 = layer3 ^ ((i * 7) % 256)

        result.append(layer4 % 256)

    return bytes(result)
'''

    namespace = {}
    exec(func_code, namespace)
    return namespace['_advanced_xor_encrypt']

def _obfuscated_decrypt_function():
    """动态生成解密函数"""
    _detect_debugging_environment()

    func_code = '''
def _advanced_xor_decrypt(data, key):
    """高级 XOR 解密"""
    result = []
    key_hash = hash(key) % 256

    for i, byte in enumerate(data):
        # 逆向多层异或
        layer4 = byte
        layer3 = layer4 ^ ((i * 7) % 256)
        layer2 = layer3 ^ key_hash
        layer1 = layer2 ^ (i % 256)

        key_char = key[i % len(key)]
        original = layer1 ^ ord(key_char)

        result.append(chr(original % 256))

    return ''.join(result)
'''

    namespace = {}
    exec(func_code, namespace)
    return namespace['_advanced_xor_decrypt']

# 延迟初始化的加密函数
_encrypt_func = None
_decrypt_func = None

def _get_encrypt_function():
    """获取加密函数"""
    global _encrypt_func
    if _encrypt_func is None:
        _encrypt_func = _obfuscated_encrypt_function()
    return _encrypt_func

def _get_decrypt_function():
    """获取解密函数"""
    global _decrypt_func
    if _decrypt_func is None:
        _decrypt_func = _obfuscated_decrypt_function()
    return _decrypt_func


def local_encrypt_payload(payload: dict) -> str:
    """本地加密载荷（增强安全版本）"""
    try:
        _detect_debugging_environment()  # 安全检查

        # 构建包含代码的完整数据结构
        full_payload = {
            "tracker_code": payload["tracker_code"],
            "config": payload["config"],
            "core_functions": payload.get("core_functions", []),
            "code": build_executable_code(payload["tracker_code"], payload["config"])
        }

        # 转换为 JSON
        json_data = json.dumps(full_payload, separators=(',', ':'))

        # 多层加密
        master_key = _get_master_key()
        encrypt_func = _get_encrypt_function()

        # 第一层：高级 XOR 加密
        layer1 = encrypt_func(json_data, master_key)

        # 第二层：位移混淆
        layer2 = bytes([(b + 17) % 256 for b in layer1])

        # 第三层：Base64 编码
        layer3 = base64.b64encode(layer2).decode('ascii')

        # 第四层：字符替换
        char_map = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                                'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210-_')
        layer4 = layer3.translate(char_map)

        # 添加前缀
        data_prefix = _get_data_prefix()
        return f"{data_prefix}{layer4}"

    except Exception as e:
        raise RuntimeError(f"本地加密失败: {e}")


def local_decrypt_payload(encrypted_data: str) -> dict:
    """本地解密载荷（增强安全版本）"""
    try:
        _detect_debugging_environment()  # 安全检查

        data_prefix = _get_data_prefix()
        if not encrypted_data.startswith(data_prefix):
            raise ValueError("无效的数据前缀")

        # 移除前缀
        layer4 = encrypted_data[len(data_prefix):]

        # 逆向第四层：字符替换
        char_map = str.maketrans('ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210-_',
                                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
        layer3 = layer4.translate(char_map)

        # 逆向第三层：Base64 解码
        layer2 = base64.b64decode(layer3.encode('ascii'))

        # 逆向第二层：位移混淆
        layer1 = bytes([(b - 17) % 256 for b in layer2])

        # 逆向第一层：高级 XOR 解密
        master_key = _get_master_key()
        decrypt_func = _get_decrypt_function()
        json_data = decrypt_func(layer1, master_key)

        # 解析 JSON
        return json.loads(json_data)

    except Exception as e:
        raise RuntimeError(f"本地解密失败: {e}")


def build_executable_code(tracker_code: str, config: dict) -> str:
    """构建可执行代码（混淆版本）"""
    try:
        _detect_debugging_environment()

        # 使用混淆的代码模板
        template = '''
# OSLisLim 保护代码（混淆版本）
import os
import sys
import hashlib
import time
import random
from datetime import datetime

# 反调试检查
def {anti_debug_func}():
    if hasattr(sys, 'gettrace') and sys.gettrace():
        raise RuntimeError("Debugging detected")

    suspicious = ['uncompyle6', 'decompyle3', 'unpyc37', 'pycdc']
    for mod in suspicious:
        if mod in sys.modules:
            raise RuntimeError(f"Analysis tool detected: {{mod}}")

# 混淆的打包检测
def {packaging_detect_func}():
    {anti_debug_func}()

    indicators = [
        hasattr(sys, 'frozen'),
        hasattr(sys, '_MEIPASS'),
        sys.executable.endswith('.exe') and 'python' not in sys.executable.lower(),
        any(temp in sys.executable.lower() for temp in ['temp', 'tmp', '_mei']),
    ]
    return any(indicators)

# 环境检查
{anti_debug_func}()
if {packaging_detect_func}():
    error_msg = """
🚫 检测到打包环境，拒绝运行！

OSLisLim 保护机制：此开源项目不允许在打包后的可执行文件中运行。
这是为了防止商业滥用和未经授权的分发。

检测到的环境特征：
- 可执行文件: {{executable}}
- 是否打包: True

如果您是合法用户，请：
1. 使用源代码方式运行：python your_script.py
2. 确保 Python 环境正确安装
3. 联系项目作者获取商业授权
""".format(executable=sys.executable)
    raise RuntimeError(error_msg.strip())

# 混淆的全局变量
{tracker_var} = None
{config_var} = {config_value}

# 追踪函数（混淆）
{tracker_code}

# 设置追踪器
{tracker_var} = {tracker_func_name}

# 混淆的保护装饰器
def {protect_decorator}(func):
    def {wrapper_func}(*args, **kwargs):
        {anti_debug_func}()
        if {tracker_var}:
            {tracker_var}(func.__name__, args, kwargs)
        return func(*args, **kwargs)
    return {wrapper_func}

# 全局保护函数引用
protect_function = {protect_decorator}

# 初始化完成
print("🔒 OSLisLim 保护已激活")
'''

        # 处理追踪代码中的函数名
        obfuscated_tracker_name = f"_tracker_func_{random.randint(1000, 9999)}"
        processed_tracker_code = tracker_code.replace("def my_tracker", f"def {obfuscated_tracker_name}")

        # 生成混淆的变量名
        variables = {
            'anti_debug_func': f"_check_{random.randint(1000, 9999)}",
            'packaging_detect_func': f"_detect_{random.randint(1000, 9999)}",
            'tracker_var': f"_tracker_{random.randint(1000, 9999)}",
            'config_var': f"_config_{random.randint(1000, 9999)}",
            'protect_decorator': f"_protect_{random.randint(1000, 9999)}",
            'wrapper_func': f"_wrapper_{random.randint(1000, 9999)}",
            'config_value': repr(config),
            'tracker_code': processed_tracker_code,
            'tracker_func_name': obfuscated_tracker_name
        }

        return _generate_obfuscated_code(template, variables)

    except Exception:
        # 降级到简单版本
        return f'''
# OSLisLim 保护代码
import os
import sys
from datetime import datetime

def detect_packaging_environment():
    indicators = [
        hasattr(sys, 'frozen'),
        hasattr(sys, '_MEIPASS'),
        sys.executable.endswith('.exe') and 'python' not in sys.executable.lower(),
    ]
    return any(indicators)

if detect_packaging_environment():
    raise RuntimeError("打包环境检测：拒绝运行")

_active_tracker = None
_active_config = {repr(config)}

{tracker_code}

_active_tracker = my_tracker

def protect_function(func):
    def wrapper(*args, **kwargs):
        if _active_tracker:
            _active_tracker(func.__name__, args, kwargs)
        return func(*args, **kwargs)
    return wrapper

print("🔒 OSLisLim 保护已激活")
'''


# 新的解密函数，用于解密整行代码
def decrypt_bundle_code(encrypted_data: str) -> str:
    """解密并返回可执行的代码（增强安全版本）"""
    try:
        _detect_debugging_environment()  # 安全检查

        # 尝试增强版本解密
        try:
            payload = local_decrypt_payload(encrypted_data)
            code = payload.get('code', '')
            if code:
                return code
        except Exception:
            pass

        # 尝试旧版本解密器（向后兼容）
        try:
            payload = _decryptor.decrypt_payload(encrypted_data)
            code = payload.get('code', '')
            if code:
                return code
        except Exception:
            pass

        raise RuntimeError("加密包中没有找到代码")

    except Exception as e:
        raise RuntimeError(f"代码解密失败: {e}")


# 本地生成保护包功能
def generate_protection_bundle(tracker_code: str = None, config: dict = None, output_file: str = "protection.oslim") -> bool:
    """生成保护包（增强安全版本）"""
    try:
        _detect_debugging_environment()  # 安全检查
        # 默认追踪代码
        if tracker_code is None:
            tracker_code = '''def my_tracker(func_name, args, kwargs):
    """默认追踪函数"""
    import json
    import os
    from datetime import datetime

    usage_data = {
        "timestamp": datetime.now().isoformat(),
        "function": func_name,
        "user_hash": hash(os.getenv("USERNAME", "unknown")) % 10000,
        "args_count": len(args),
        "has_kwargs": len(kwargs) > 0
    }

    log_file = "usage_tracking.json"
    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {"usage_records": []}

        existing_data["usage_records"].append(usage_data)

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)

        print(f"📊 [追踪] 记录函数调用: {func_name}")

    except Exception as e:
        print(f"⚠️ [追踪] 记录失败: {e}")'''

        # 默认配置
        if config is None:
            config = {
                "project_name": "我的开源项目",
                "author": "项目作者",
                "protection_level": "standard",
                "offline_mode": False,
                "license_file": "LICENSE",
                "core_functions": ["main", "process_data", "save_result"]
            }

        print("🔒 正在生成 OSLisLim 保护包...")

        # 准备载荷
        payload = {
            "tracker_code": tracker_code,
            "config": config,
            "core_functions": config.get("core_functions", [])
        }

        # 本地加密
        encrypted_data = local_encrypt_payload(payload)

        # 生成包
        bundle_content = f"exec(__import__('oslislim.crypto_client',fromlist=['decrypt_bundle_code']).decrypt_bundle_code('{encrypted_data}'))"

        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(bundle_content)

        print(f"✅ 保护包已生成: {output_file}")
        print(f"   包大小: {len(bundle_content)} 字符")
        print(f"   加密数据长度: {len(encrypted_data)} 字符")

        return True

    except Exception as e:
        print(f"❌ 生成保护包失败: {e}")
        return False


def create_default_tracker() -> str:
    """创建默认追踪函数代码"""
    return '''def my_tracker(func_name, args, kwargs):
    """默认追踪函数"""
    import json
    import os
    from datetime import datetime

    usage_data = {
        "timestamp": datetime.now().isoformat(),
        "function": func_name,
        "user_hash": hash(os.getenv("USERNAME", "unknown")) % 10000,
        "args_count": len(args),
        "has_kwargs": len(kwargs) > 0
    }

    log_file = "usage_tracking.json"
    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {"usage_records": []}

        existing_data["usage_records"].append(usage_data)

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)

        print(f"📊 [追踪] 记录函数调用: {func_name}")

    except Exception as e:
        print(f"⚠️ [追踪] 记录失败: {e}")'''


def create_default_config() -> dict:
    """创建默认配置"""
    return {
        "project_name": "我的开源项目",
        "author": "项目作者",
        "protection_level": "standard",
        "offline_mode": False,
        "license_file": "LICENSE",
        "core_functions": ["main", "process_data", "save_result"]
    }


# 兼容性函数
def initialize_protection(bundle_file: str = None, encrypted_data: str = None):
    """初始化保护机制"""
    if bundle_file:
        return decrypt_and_execute(bundle_file)
    elif encrypted_data:
        return decrypt_and_execute_bundle(encrypted_data)
    else:
        raise ValueError("必须提供 bundle_file 或 encrypted_data")
