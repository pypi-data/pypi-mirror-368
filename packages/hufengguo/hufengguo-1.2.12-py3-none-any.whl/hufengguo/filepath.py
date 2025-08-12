from os import access, chmod, getcwd, remove, sep as ossep, W_OK
from os.path import exists, isabs, isdir, isfile, join
from shutil import rmtree
from stat import S_IREAD, S_IWRITE
from sys import platform as osname
import re



#----------------------------------------------------------------
# 自定义函数
#
# 函数名：
#     my_exists
#
# 功能：
#     判定路径是否存在
#     若路径名的最后一个字符是空格，则os.path.exists()判定失败，本函数能成功
#
# 参数说明：
#     fp：想要判定的路径名
#
# 返回值说明：
#     True, "file" ：存在，是文件
#     True, "dir"  ：存在，是目录
#     False, ""    ：不存在
#
# 调用示例：
#     fp = r"Q:\abc \123\xyz "
#     flag, msg = my_exists(fp)
#     print(flag, msg)
#
#----------------------------------------------------------------
def my_exists(fp):
    # print(fp)
    if osname == "win32" and re.findall(rf"\s\\", fp+"\\"):
        fp = fp if isabs(fp) else join(getcwd(), fp)
        fp = getcwd()[:2] + fp if fp.startswith(ossep) else fp
        fp = rf"\\?\{fp}"
    # print(fp)
    if not exists(fp):
        flag, msg = False, ""
    elif isfile(fp):
        flag, msg = True, "file"
    else:
        flag, msg = True, "dir"
    return flag, msg



#----------------------------------------------------------------
# 自定义函数
#
# 函数名：
#     my_shutil_rmtree
#
# 功能：
#     删除目录，比shutil.rmtree()功能更强
#     若目录名的某级目录最后一个字符是空格，则shutil.rmtree()删除失败，本函数能成功
#
# 参数说明：
#     p：想要删除的目录
#
# 返回值说明：
#     True  ：成功删除
#     False ：成功删除
#     None  ：目录不存在
#
# 调用示例：
#     p = r"Q:\abc \123\xyz "
#     flag = my_shutil_rmtree(p)
#     print(flag)
#
#----------------------------------------------------------------
def my_shutil_rmtree(p):
    # 回调函数，处理删除错误
    # func: 导致异常的函数（os.remove 或 os.rmdir）
    # fp: 引发异常的目录名或文件名
    # exc_info: sys.exc_info() 返回的异常信息
    def handle_rmtree_error(func, fn, exc_info):
        # print(func, fn, exc_info)
        # 如果是读写权限错误，尝试去掉文件的只读属性后重试
        if not access(fn, W_OK):
            chmod(fn, S_IWRITE)  # 去掉只读属性
            func(fn)             # 重试删除操作
        else:
            raise  # 如果不是权限错误，重新抛出异常

    newp = p if isabs(p) else join(getcwd(), p)
    newp = getcwd()[:2] + newp if newp.startswith(ossep) else newp
    # print(newp)
    if osname == "win32":
        newp2 = rf"\\?\{newp}"
    else:
        newp2 = newp
    # print(newp2)

    if not isdir(newp2):
        return None
    try:
        rmtree(newp2, onerror=handle_rmtree_error)
        flag = True
    except Exception as e:
        print(e)
        flag = False

    return flag



#----------------------------------------------------------------
# 自定义函数
#
# 函数名：
#     my_os_remove
#
# 功能：
#     删除文件，比os.remove()功能更强
#     若文件名的某级目录最后一个字符是空格，则os.remove()删除失败，本函数能成功
#
# 参数说明：
#     p：想要删除的文件
#
# 返回值说明：
#     True  ：成功删除
#     False ：成功删除
#     None  ：目录不存在
#
# 调用示例：
#     fn = r"Q:\abc \123\xyz \test.txt"
#     flag = my_os_remove(fn)
#     print(flag)
#
#----------------------------------------------------------------
def my_os_remove(fn):
    newfn = fn if isabs(fn) else join(getcwd(), fn)
    newfn = getcwd()[:2] + newfn if newfn.startswith(ossep) else newfn
    if osname == "win32" and re.findall(rf"\s\\", newfn+"\\"):
        newfn2 = rf"\\?\{newfn}"
    else:
        newfn2 = newfn

    if not isfile(newfn2):
        return None

    if not access(newfn2, W_OK):
        chmod(newfn2, S_IWRITE)
    try:
        remove(newfn2)
        flag = True
    except Exception as e:
        print(e)
        flag = False
    return flag

