from setuptools import setup, find_packages
import io

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PyFeishuGroupBot',
    version='0.0.7',
    install_requires=['requests'],
    packages=find_packages(),
    include_package_data=True,
    package_data={'PyFeishuGroupBot': ['plugin/*']},
    url='https://github.com/Moxin1044/Py-FeishuGroupBot',
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Moxin',
    author_email='1044631097@qq.com',
    description='Python的飞书群组机器人调用方法集合'
)