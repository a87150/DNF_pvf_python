# -*- coding: utf-8 -*-
'''config 下 JSON 的兼容读取：老配置是 GBK（中文 Windows 上由 locale 写出来的），
新写的必须是 UTF-8。py3.14 起默认 UTF-8 模式，但打包/直接跑仍可能落到 locale 编码，
写死任何一种都会有人读不出来，所以按 utf-8-sig -> utf-8 -> gbk 依次尝试。

单独一个模块是为了避开 appCommon <-> cacheManager/pvfReader 的循环 import：
pvfReader 在 import 时（模块级）就要读 pvfKeywords*.json。'''
import json


def loadJsonFile(path):
    with open(path,'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig','utf-8','gbk'):
        try:
            return json.loads(raw.decode(enc))
        except BaseException:
            continue
    return json.loads(raw.decode('utf-8',errors='replace'))
