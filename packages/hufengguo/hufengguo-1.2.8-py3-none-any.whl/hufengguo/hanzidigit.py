# 导入
import re


#----------------------------------------
# 常量
#----------------------------------------

# 中文数字每四位一组的组名和权重
node ="极载正涧沟穰秭垓京兆亿万"                                # 传统名称，例如：一兆、一京
wanyinode = "亿万"                                              # 现代名称，例如：一万亿、一亿亿
node_weight = {e: 10**((12-i)*4) for i, e in enumerate(node)}   # 传统权重，万=10**4，兆=10**12，京=10**16
digits = "一二三四五六七八九"                   # 不含零的汉字数字字符
digi_weight = dict(zip(digits, range(1, 10)))   # 不含零的汉字数字字符对应的数字
digits_with_zero = "零一二三四五六七八九"       # 含零的汉字数字字符

# 关于人民币金额正常写法和大写写法互转的常量和函数
xiaoxie = "零一二三四五六七八九十百千万亿兆京垓秭穰沟涧正载极"
daxie   = "零壹贰叁肆伍陆柒捌玖拾佰仟萬億兆京垓秭穰溝澗正載極"
m_xiao2da = str.maketrans(xiaoxie[1:13], daxie[1:13])
m_da2xiao = str.maketrans(daxie, xiaoxie)


#----------------------------------------
# 自定义函数
#----------------------------------------

# 人民币金额正常汉字写法变大写写法只需要变一二三四五六七八九十百千就行
# 万和亿不需要变，类推之下，比亿大的计数等级也不需要变
def xiao2da(s):
    return s.translate(m_xiao2da)


# 人民币金额大写写法变正常汉字写法，本应该是正常变大写的逆运算，
# 但为了防止万和万以上的计数等级传入繁体汉字，
# 这里列出所有的对应的字符，包括转换前后一样的字符
def da2xiao(s):
    return s.translate(m_da2xiao)


# 数字分节，默认四位一组，空格分隔
def fenjie_nummber(i, group=4, sep=None):
    if not isinstance(i, int) or group<=0:
        return str(i)
    i, flagchar = (-i, "-") if i<0 else (i, "")
    if group==3:
        r = format(i, ",")
        if sep != None and sep != ',':
            r = r.replace(",", sep)
    else:
        slist, si = [], str(i)
        while si:
            slist.insert(0, si[-group:])
            si = si[:-group]
        sep = " " if not sep else str(sep)
        r = flagchar + sep.join(slist)
    return r


# 汉字转数字（10的97次方以内）
def hanzi2digit(s):
    # 预处理：把常见的汉字整数简称变成全称
    def pre_process(s):
        s = da2xiao(s)
        s = re.sub(r"^十", r"一十", s)
        # print(1, s)
        s = re.sub(rf"两([{node}千百])", r"二\1", s)
        # print(2, s)
        s = re.sub(rf"万([{digits}])$", r"万\1千", s)
        # print(3, s)
        s = re.sub(rf"千([{digits}])$", r"千\1百", s)
        # print(4, s)
        s = re.sub(rf"百([{digits}])$", r"百\1十", s)
        # print(5, s)
        return s

    # 基本情况：万以内的汉字转数字
    def hanzi2digit_4(s):
        m = re.findall(rf"^([{digits}]千)?([{digits}]百)?零?([{digits}]?十)?([{digits}])?$", s)
        # print("hanzi2digit_4", s, m)
        if m:
            q, b, s, g = m[0]
            r = digi_weight.get(q.rstrip("千"), 0)*1000 + \
                digi_weight.get(b.rstrip("百"), 0)*100 + \
                digi_weight.get(s.rstrip("十"), 0)*10 + \
                digi_weight.get(g, 0)
            return r
        else:
            return -1

    # 递归函数：汉字转数字
    def _hanzi2digit(s):
        if not s:
            return 0
        
        poslist = list(map(lambda e: s.find(e)!=-1, node))
        # print(poslist)
        if not any(poslist):
            return hanzi2digit_4(s)
        else:
            pos = poslist.index(True)
            nodechar = node[pos]
            # print(pos, nodechar)
            index = s.rfind(nodechar)
            # print(index, s[:index], s[index], s[index+1:])
            if s[:index]:
                left = hanzi2digit(s[:index])
                right = hanzi2digit(s[index+1:].lstrip("零"))
                # print(left, right)
                if left>=0 and right>=0:
                    return left*node_weight[s[index]]+right
                else:
                    return -1
            else:
                return -1

    # 预处理
    s = pre_process(s)
    # print(s)

    # 返回递归调用的结果    
    return _hanzi2digit(s)


# 数字转汉字
def digit2hanzi(n, wanyiflag=False, daxieflag=False):
    # 基本情况：万以内的正整数转汉字
    def _digit2hanzi_4(n):
        s = "".join(["".join(e) for e in zip(map(lambda e: digits_with_zero[int(e)], f"{n:04}"), ("千", "百","十", ""))])
        s = re.sub(r"零[千百十]", r"零", s)
        s = re.sub(r"零+", r"零", s).strip("零")
        s = re.sub(r"^一十", r"十", s)
        return s

    if not isinstance(n, int) or n<0:
        return ""
    elif n == 0:
        return "零"

    thenode = wanyinode if wanyiflag else node
    sn, count, weightchar, sresult = str(n), 0, "", ""
    # print(sn)
    while sn:
        sn, scur = sn[:-4], sn[-4:]
        # print(sn, scur)
        iright = int(scur)
        if iright==0:
            right_result = "零" + (weightchar if wanyiflag and count<0 and count%len(thenode)==0 else "")
        elif scur[0]=='0':
            right_result = "零" + _digit2hanzi_4(int(scur)) + weightchar
        else:
            right_result = _digit2hanzi_4(int(scur)) + weightchar
        sresult = right_result + sresult
        # print(sn, scur, sresult)
        count = count-1 if count>-len(thenode) else -1
        weightchar = thenode[count]
    # print(sresult)
    sresult = sresult.replace("零万", "零").replace("零十", "零一十")
    sresult = re.sub(r"零+", r"零", sresult).replace("零亿", "亿").strip("零")
    if daxieflag:
        sresult = xiao2da(sresult)
    return sresult


r"""
《数术记遗》是中国古代数学经典著作，由东汉徐岳编撰、北周汉中郡守甄鸾注释，其中提出了中国的大数系统：

黄帝为法，数有十等，及其用也，乃有三焉。十等者谓亿、兆、京、垓、秭、穰、沟、涧、正、载，三等者谓上中下也。其下数者，十十变之，若言十万曰亿、十亿曰兆、十兆曰京也。中数者，万万变之，若言万万曰亿、万万亿曰兆、万万兆曰京也。上数者数穷则变，若言万万曰亿、亿亿曰兆、兆兆曰京也。下数浅短，计事则不尽，上数宏廓，世不可用，故其传业惟以中数耳。

在《数术记遗》提出的“亿兆京垓秭穰沟涧正载”这十等数词之后，网上还流传着一些数词：极、恒河沙、阿僧袛、那由它、不可思议、无量、大数。除了“极”之外，这些都是多个汉字表示数的等级，这里不予采信，仅加入“极”字放在“载”之后作为最大的数词等级。

本扩展库采用的大数等级体系包含12等（在十等之前加入“万”，之后加入“极”）：

万：代表的是10的4次方。（wàn）
亿：代表的是10的8次方。（yì）
兆：代表的是10的12次方。（zhào）
京：代表的是10的16次方。（jīng）
垓：代表的是10的20次方。（gāi）
秭：代表的是10的24次方。（zǐ）
穰：代表的是10的28次方。（ráng）
沟：代表的是10的32次方。（gōu）
涧：代表的是10的36次方。（jiàn）
正：代表的是10的40次方。（zhèng）
载：代表的是10的44次方。（zǎi）
极：代表的是10的48次方。（jí）

调用方法：
from hufengguo import digit2hanzi, hanzi2digit, xiao2da, da2xiao, fenjie_nummber

# 测试汉字转数字
print(hanzi2digit("一百二十三"))                      # 输出：123
print(hanzi2digit("壹佰贰拾叁"))                      # 输出：123
print(hanzi2digit("三兆"))                            # 输出（3后面12个0）：3000000000000
print(hanzi2digit("三万亿"))                          # 输出（3后面12个0）：3000000000000

# 测试数字转汉字
print(digit2hanzi(123))                               # 输出：一百二十三
print(digit2hanzi(123, daxieflag=True))               # 输出：壹佰贰拾叁
print(digit2hanzi(3*10**12))                          # 输出：三兆
print(digit2hanzi(3*10**12, wanyiflag=True))          # 输出：三万亿
print(digit2hanzi(1234500000000))                     # 输出：一兆二千三百四十五亿
print(digit2hanzi(1234500000000, wanyiflag=True))     # 输出：一万二千三百四十五亿
print(digit2hanzi(12345000000000000))                 # 输出：一京二千三百四十五兆
print(digit2hanzi(12345000000000000, wanyiflag=True)) # 输出：一亿二千三百四十五万亿

# 测试汉字数字正常写法和大写写法互转
print(xiao2da("一万二千三百零六"))                    # 输出：壹万贰仟叁佰零陆
print(da2xiao("壹万贰仟叁佰零陆"))                    # 输出：一万二千三百零六

# 测试数字分节
print(fenjie_nummber(12345678901, group=3))           # 输出：12,345,678,901
print(fenjie_nummber(12345678901, group=3, sep="_"))  # 输出：12_345_678_901
print(fenjie_nummber(12345678901))                    # 输出：123 4567 8901
print(fenjie_nummber(12345678901, group=4))           # 输出：123 4567 8901
print(fenjie_nummber(12345678901, group=5, sep=","))  # 输出：123,4567,8901
print(fenjie_nummber(-1234567))                       # 输出：-123 4567

"""