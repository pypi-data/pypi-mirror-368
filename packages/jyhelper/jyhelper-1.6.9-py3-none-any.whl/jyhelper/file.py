#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2023/11/14 14:03 
# @Author : JY
"""
文件操作相关
有些文件中文会报错，可以尝试encoding=‘gbk’
"""

import os
import shutil
import hashlib


class file:
    ENCODING_UTF8 = 'utf-8'
    ENCODING_GBK = 'gbk'

    def __init__(self):
        pass

    # 一次性读取txt文件的全部内容
    @staticmethod
    def readTxtFile(filePath, encoding=ENCODING_UTF8):
        with open(filePath, 'r', encoding=encoding) as f:
            content = f.read()
        return content

    # 按行读取txt的内容,返回一个生成器对象，如果想要数组结果，可以使用list把结果转一下：list(file.readTxtFileByLine('x.txt'))
    @staticmethod
    def readTxtFileByLine(filePath, encoding=ENCODING_UTF8):
        with open(filePath, 'r', encoding=encoding) as f:
            # 按行读取内容
            line = f.readline()
            while line:
                # 去除换行符并处理每行内容
                line = line.strip()
                # 打印每行内容或进行其他操作
                yield line
                line = f.readline()

    # 以追加的形式写文件
    @staticmethod
    def writeTxtFileAppendMode(filePath, content, encoding=ENCODING_UTF8, newline="\n"):
        with open(filePath, 'a', encoding=encoding, newline=newline) as f:
            f.write(content)

    # 清空文件后写入
    @staticmethod
    def writeTxtFileNewMode(filePath, content, encoding=ENCODING_UTF8, newline="\n"):
        with open(filePath, 'w', encoding=encoding, newline=newline) as f:
            f.write(content)

    # 得到文件的行数
    @staticmethod
    def countLines(filePath, encoding=ENCODING_UTF8):
        with open(filePath, 'r', encoding=encoding) as f:
            line_count = sum(1 for line in f)
        return line_count

    """
    重命名文件
    shutil.move(fileName, newFileName) # 会覆盖已有的文件
    os.rename(fileName,newFileName) # 不会覆盖，并且会报异常
    """

    @staticmethod
    def renameFile(fileName, newFileName, fuGai=True):
        try:
            if fuGai:
                shutil.move(fileName, newFileName)
            else:
                os.rename(fileName, newFileName)
            return True
        except Exception as e:
            print(str(e))
            return False

    # 删除文件或者文件夹
    @staticmethod
    def delFile(fileName):
        try:
            if os.path.isdir(fileName):
                shutil.rmtree(fileName)
                return True
            elif os.path.isfile(fileName):
                os.remove(fileName)
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False

    # 是否是目录
    @staticmethod
    def isDir(fileName):
        return os.path.isdir(fileName)

    # 是否是文件
    @staticmethod
    def isFile(fileName):
        return os.path.isfile(fileName)

    # 创建目录
    @staticmethod
    def mkdir(directory):
        try:
            # 创建目录
            os.makedirs(directory)
            return True
        except FileExistsError:
            return True
        except OSError as e:
            print(f"创建目录 '{directory}' 失败：{e}")
            return False

    @staticmethod
    def getFileMd5(file_path):
        """计算单个文件的 MD5 值"""
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            # 逐块读取文件内容进行加密计算
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @staticmethod
    def getFolderMd5(folder_path):
        """计算文件夹的 MD5 值"""
        md5_hash = hashlib.md5()

        # 递归遍历文件夹中的所有文件
        for root, dirs, files in os.walk(folder_path):
            dirs.sort()
            files.sort()
            for fileName in files:  # 按文件名排序，确保一致性
                file_path = os.path.join(root, fileName)
                # 计算文件的 MD5 值并更新到文件夹 MD5 值中
                file_md5 = file.getFileMd5(file_path)
                md5_hash.update(file_md5.encode(file.ENCODING_UTF8))  # 合并文件 MD5
        return md5_hash.hexdigest()

    @staticmethod
    def listFolderFiles(folder_path):
        """列出文件夹以及子文件夹中的文件"""
        for root, dirs, files in os.walk(folder_path):
            dirs.sort()
            files.sort()
            for fileName in files:  # 按文件名排序，确保一致性
                file_path = os.path.join(root, fileName)
                yield file_path


if __name__ == '__main__':
    file.writeTxtFileNewMode('a.log',content="sdfsdf\nsdfsd好的f\na\n")
