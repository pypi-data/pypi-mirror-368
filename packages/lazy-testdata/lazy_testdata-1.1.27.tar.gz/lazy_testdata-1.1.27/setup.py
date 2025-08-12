from setuptools import setup, find_packages

setup(
    name='lazy_testdata',  # 必须是唯一的
    version='1.1.27',
    author='YuWeiPeng',
    author_email='404051211@qq.com',
    description='testdata include chinese personal four element and offen use datetime 测试数据包含随机生成的中国公民四要素，及常用的日期时间 根据swagger文档生成规则用例 用于性能测试摸高，并生成统一测试报告',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.cnblogs.com/yicaifeitian',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'json2html>=1.3.0',
        'pandas>=2.3.1',
        'python-dateutil>=2.9.0',
        'records>=0.6.0',
        'requests>=2.32.4',
        'setuptools>=80.9.0',
        'SQLAlchemy>=2.0.41',
    ],
)