from setuptools import setup, find_packages

setup(
    name='s3_sdk',
    version='0.1.3',
    packages=find_packages(),
    install_requires=['boto3>=1.26.0'],
    author='Giatti Chen',
    author_email='chenjieting@baidu.com',
    description='A simple SDK for interacting with AWS S3',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/GiattiChen',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

'''
📦 发布为 pip 包

1.	创建项目结构：
s3_sdk/
├── s3_sdk/
│   └── __init__.py
├── setup.py
├── LICENSE
└── README.md

s3_sdk/
├── s3_sdk/
│   ├── __init__.py
│   ├── s3_client.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_s3_client.py
├── setup.py
├── README.md
└── requirements.txt

2.	编写 setup.py：
本文件内容

3.	编写 README.md：
同目录下 README.md 文件

4.	生成分发包：
python setup.py sdist bdist_wheel

5.	上传到 PyPI：
pip install twine
twine upload dist/*

6.	安装并使用：
pip install s3_sdk

‘’‘python
from s3_sdk import S3SDK

s3_sdk = S3SDK(region='ap-northeast-1')
# 使用 s3_sdk 进行 S3 操作
‘’‘


更新sdk
1.确保更新了对应的版本号（比如从 0.1.0 改成 0.1.1）在 setup.py 里：
setup(
    name='s3_sdk',
    version='0.1.1',  # 版本号更新
    # 其他保持不变
)
# 如果你不改版本号，上传时 PyPI 会提示版本已存在，且 pip 不会自动升级。

2. 重新打包
在项目根目录运行：
python setup.py sdist bdist_wheel
这会在 dist/ 目录生成新的 .tar.gz 和 .whl 文件 (注意删除原来的文件)

3. 上传到 PyPI
pip install --upgrade twine
twine upload dist/*

4. 升级安装
pip install --upgrade s3_sdk

5. 测试
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pip install --index-url https://test.pypi.org/simple/ s3_sdk
'''