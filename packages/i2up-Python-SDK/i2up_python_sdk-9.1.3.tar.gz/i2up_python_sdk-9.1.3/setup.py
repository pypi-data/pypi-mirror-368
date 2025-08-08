import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="i2up_Python_SDK", # 模块名称
    version = "9.1.3", # 当前版本
    author="wanghl", # 作者
    author_email="wanghl@info2soft.com", # 作者邮箱
    description="英方统一数据管理平台python版本SDK", # 简短介绍
    long_description="英方统一数据管理平台python版本SDK", # 模块详细介绍
    long_description_content_type="text/markdown", # 模块详细介绍格式
    packages=setuptools.find_packages(), # 自动找到项目中导入的模块
    # 模块相关的元数据(更多描述信息)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Artistic License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=[
        'numpy',
        'requests',
        'simplejson',
        'pytest',
        'flake8',
        'rsa',
        'crypto',
        'pycryptodome',
        'pyopenssl'
    ],
    python_requires=">=3",
    # url="https://gitee.com/i2soft/i2up-python-sdk", # gitee地址
)