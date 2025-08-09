import base64
import hashlib
import random
import time

from Crypto.Cipher import AES


def ts_current_ts() -> str:
    """获取当前时间戳(毫秒)
    :return: 当前时间戳（毫秒）
    """
    return str(int(time.time() * 1000))


def encrypt_md5_hex(string: str) -> str:
    """获取十六进制加密字符串
    :param string: 要加密的字符串
    :return: 十六进制字符串
    """
    hex_str = hashlib.md5(string.encode('utf-8')).hexdigest()
    return hex_str


def generate_imei() -> str:
    """生成imei码
    :return: str
    """
    tac = ''.join(random.choices('0123456789', k=6))
    fac = ''.join(random.choices('0123456789', k=2))
    snr = ''.join(random.choices('0123456789', k=6))

    imei_base = tac+fac+snr
    imei_list = [int(digit) for digit in imei_base]
    check_digit = sum(imei_list[::-2] + [sum(divmod(d * 2,10)) for d in imei_list[-2::-2]]) % 10

    imei = imei_base + str((10 - check_digit) % 10)
    return imei


def encrypt_3DES_CBC(data: str, key: bytes, iv: bytes):
    """3DES算法 CBC加密模式
    :param data: 原始字符串
    :param key: 密钥(16字节) b'6d6656a37cdb7977c10f6d83cab168e9'
    :param iv: 初始化向量(16字节) b'0000000000000000'
    :return:
    """
    # 创建AES密码对象
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 填充数据
    p_bytes = data.encode('utf-8')
    # 计算需要填充的字节数
    pad_len = AES.block_size - (len(p_bytes) % AES.block_size)
    # 使用填充字节进行填充
    padding = bytes([pad_len] * pad_len)
    padded_data = p_bytes + padding

    # 加密数据
    encrypted_data = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_data).decode('utf-8')
