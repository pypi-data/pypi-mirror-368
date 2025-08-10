import os

from setuptools import setup, find_packages

# 读取requirements.txt文件
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="publicmodel",
    version="3.4.8",
    packages=find_packages(),
    install_requires=requirements,
    author="YanXinle",
    author_email="1020121123@qq.com",
    description="作者: YanXinle",
    url="https://github.com/Yanxinle1123/LeleComm",
)
