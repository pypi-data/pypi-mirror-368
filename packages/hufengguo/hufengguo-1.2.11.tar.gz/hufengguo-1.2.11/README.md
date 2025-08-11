# 扩展库介绍

这是中国传媒大学胡凤国老师上课分享的自定义函数库，其中包含几个常用的文本处理函数。发布本扩展库主要是方便上课学生练习Python程序，顺便分享给其他需要的Pythoner。

刚学会发布扩展库，PyPI很多东西还不熟，如有问题，请多提宝贵意见。


# 安装说明

pip install -U hufengguo


# 用法说明

具体用法见胡凤国老师的上课教材：《Python程序设计（基于计算思维和新文科建设）》，ISBN：9787121435577，胡凤国，电子工业出版社，2022年6月。

这里举一些简单的例子。


## 产生1到100之内的素数

```
# 导入
from hufengguo import isprime

# 产生素数列表
x = [i for i in range(101) if isprime(i)]

# 输出
print(x)
```

## 去掉多行文本中的空白行和每行首尾空白符

```
# 导入
from hufengguo import remove_white_from_text

# 赋值
s = " 12345\t\n  上山打老虎\n \n\n"

# 变换
t = remove_white_from_text(s)

# 输出
print("字符串s：", "-"*20, s, "-"*20, "\n字符串t：", "-"*20, t, "-"*20, sep="\n")
```

## 调用jieba扩展库对一个文本文件进行分词和词性标注

```
# 导入
from hufengguo import segtag_by_jieba

# 对单文件进行分词和词性标注操作
segtag_by_jieba(r"in.txt", r"out.txt")
```
本函数会自动判断文本文件的编码并进行读取，生成文件的默认编码是utf-8-sig。


## 调用jieba扩展库对一个目录下的文本文件进行分词和词性标注

```
# 导入
from hufengguo import my_path2path, segtag_by_jieba

# 批量进行分词和词性标注操作
my_path2path(r"in", [".txt"], r"out", segtag_by_jieba)
```
本函数会自动搜索目录及子目录下的所有文本文件，进行分词和词性标注操作之后保存到目标目录，目标目录会保持跟源目录相同的目录结构。

本库提供的函数my_path2path()功能很强，它把目录对目录的多文件操作转化为单文件对单文件的操作。第二个参数可以换成其它的扩展名，第四个参数是一个函数名，我们可以换成其它的自定义函数来完成其它文本处理任务（要求自定义函数具有两个参数，第1个参数是源文件名，第2个参数是目标文件名，自定义函数的功能是对源文件进行自定义操作，操作结果写入目标文件）。


## 数字与汉字读法互转

本库采用我国传统数学的大数体系：零一二三四五六七八九十百千万亿兆京垓秭穰沟涧正载极。从十开始，逢十进位；从万开始，逢万进位，1兆等于1万亿（10的12次方），1京等于1万兆（10的16次方），……，1极等于1万载（10的48次方），传统大数体系可以表示长达96位数字。本库既支持长达96位数字的传统大数体系，又支持目前只通过万和亿循环的大数表示方法。

```
# 导入
from hufengguo import digit2hanzi, hanzi2digit

# 汉字转数字
print(hanzi2digit("一百二十三"))
print(hanzi2digit("壹佰贰拾叁"))
print(hanzi2digit("三兆")
print(hanzi2digit("三万亿"))

# 数字转汉字
print(digit2hanzi(123))
print(digit2hanzi(123, daxieflag=True))
print(digit2hanzi(3*10**12))
print(digit2hanzi(3*10**12, wanyiflag=True))
print(digit2hanzi(1234500000000))
print(digit2hanzi(1234500000000, wanyiflag=True))
print(digit2hanzi(12345000000000000))
print(digit2hanzi(12345000000000000, wanyiflag=True))

```

## 人民币金额的正常汉字写法与大写写法互转

```
# 导入
from hufengguo import xiao2da, da2xiao

# 转换
print(xiao2da("一万二千三百零六"))
print(da2xiao("壹万贰仟叁佰零陆"))
```

## 分节格式化数字

```
# 导入
from hufengguo import fenjie_nummber

# 分节格式化操作
print(fenjie_nummber(12345678901, group=3))
print(fenjie_nummber(12345678901, group=3, sep="_"))
print(fenjie_nummber(12345678901))
print(fenjie_nummber(12345678901, group=4))
print(fenjie_nummber(12345678901, group=5, sep=","))
print(fenjie_nummber(-1234567))
```

## 创建目录、删除文件和目录

本库给出的函数功能比os.makedirs()、os.remove()和shutil.rmtree()都要好，它们都处理不了目录名的最后一个字符是空格的情况，但本库给出的三个函数是可以的，具体请看代码示例。

```
# 导入
from os import chmod
from os.path import exists
from stat import S_IREAD
from hufengguo import make_dir_exists, my_os_remove, my_shutil_rmtree

# 创建目录(123后面有个空格)
# 注意os.makedirs(r"abc\123 ")创建的目录123后面没有空格
fn = r"abc\123 \test.txt"
print(make_dir_exists(fn, fileflag=True))

# 生成文件
with open(fn, "wt") as fpw:
    fpw.write("上山打老虎")

# 为文件添加只读属性
chmod(fn, S_IREAD)

# 删除文件（注意os.remove(fn)会报错）
print(exists(fn))
print(my_os_remove(fn))
print(exists(fn))

# 删除目录（注意shutil.rmtree(r"abc")会报错）
print(exists(r"abc"))
flag = my_shutil_rmtree(r"abc")
print(flag)
print(exists(r"abc"))
```
