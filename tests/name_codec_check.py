# 角色名编解码回归自检：decode() / getCharactorNo 都不能再损坏或崩
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dnfpkgtool.sqlManager2 import decode
import dnfpkgtool.sqlManager2 as S

def check(name, cond):
    print(('PASS  ' if cond else 'FAIL  ') + name)
    if not cond:
        sys.exit(1)

n = '阿修罗'
check('正常 unicode 原样返回', decode(n) == n)
check('正常 unicode 不产生 ?', '?' not in decode(n))
check('正常 unicode 多字节不乱', decode('測試汉字') == '測試汉字')
check('cp1252 形态(MySQL latin1) 能还原', decode(n.encode('utf-8').decode('cp1252')) == n)
check('latin1 形态能还原', decode(n.encode('utf-8').decode('latin1')) == n)
check('含 0x80-0x9F 的字能还原', decode('你好'.encode('utf-8').decode('cp1252')) == '你好')
check('ascii 原样', decode('abc123') == 'abc123')
check('空串', decode('') == '')
check('已是坏数据的字符串不再恶化', decode('阿?罗') == '阿?罗')
check('坏字节不抛异常', isinstance(decode(b'\xe9?\xbf'.decode('latin1')), str))
check('写回字节 = utf-8(原样)', n.encode('utf-8') == b'\xe9\x98\xbf\xe4\xbf\xae\xe7\xbd\x97')

# getCharactorNo：默认索引 0 = '混合' 曾被当编码名用 → LookupError
calls = []
def fake(db, sql, args=None, charset='utf8'):
    calls.append((sql, args, charset))
    return [(7,)]
S.execute_and_fetch = fake
try:
    r = S.getCharactorNo(n)
    ok = True
except Exception as e:
    ok = False
    r = repr(e)
check('getCharactorNo 不再抛异常(原为 LookupError)', ok)
check('改成参数化查询（不再拼串）', bool(calls) and all('%s' in c[0] and c[1] for c in calls))
check('两种连接字符集都查了', {'latin1', 'utf-8'} <= {c[2] for c in calls})
check('返回值形状仍是 [0][0]', bool(r) and r[0][0] == 7)
print('NAME_CODEC_CHECK PASSED')
