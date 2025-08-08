# -*- coding: utf-8 -*-
import hashlib
from urllib import parse

####################### md5 sign #######################
def md5_sign(attributes, mct_key):
    # _logger.warning(f'attributes for md5 sign: {attributes}')
    attributes_new = {k: attributes[k] for k in sorted(attributes.keys()) if
                      attributes[k] is not None and k != 'stream_url'}
    # print(f'attributes_new@md5 sign: {attributes_new}')
    # sign_str = "&".join(
    #     [f"{sk}={attributes_new[sk]}" for sk in attributes_new.keys()]
    # )
    sign_str = parse.urlencode(attributes_new)
    # print(f'sign_str@md5 sign: {sign_str}')
    return (
        hashlib.md5((sign_str + "&key=" + mct_key).encode(encoding="utf-8"))
        .hexdigest()
        .upper()
    )


####################### sha-256 sign #######################
def sha256_sign(attributes, api_key):
    """ 生成 SHA-256 签名 """
    # 1. 过滤非空参数并排序
    attributes_new = {
        k: attributes[k]
        for k in sorted(attributes.keys())
        if attributes[k] is not None
    }

    # 2. 生成待签名字符串（保持 urlencoded 编码规范）
    # sign_str = parse.urlencode(attributes_new)
    # 生成待签名字符串（保持空格不被编码）
    def custom_quote(value):
        return parse.quote(value, safe="").replace("%20", " ")

    sign_str = "&".join(
        f"{custom_quote(str(k))}={custom_quote(str(v))}" for k, v in attributes_new.items()
    )
    print(f"sign_str: {sign_str}")

    # 3. 拼接密钥并生成 SHA-256 签名
    raw_sign = f"{sign_str}&key={api_key}".encode("utf-8")
    print(f"raw_sign: {raw_sign}")
    sign_code = hashlib.sha256(raw_sign).hexdigest().upper()
    print(f"sign_code: {sign_code}")
    return sign_code
