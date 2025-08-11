from setuptools import setup, find_packages

setup(
    name='QitianSDK',
    version='0.2.2',
    keywords=['qitian', 'SmartDjango'],
    description='方便SmartDjango部署的齐天簿SDK',
    long_description='提供齐天簿OAuth2.0接口等',
    license='MIT Licence',
    url='https://github.com/Jyonn/QitianSDK',
    author='Jyonn Liu',
    author_email='i@6-79.cn',
    platforms='any',
    packages=find_packages(),
    install_requires=[
        'smartdjango>=4.2.1',
        'requests',
        'oba'
    ],
)
