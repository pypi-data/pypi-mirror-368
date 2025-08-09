from setuptools import setup, find_packages

setup(
    name="NeZha2",
    version="0.1.2",
    packages=find_packages(),
    package_data={
        'nezha2': ['*.txt']
    },
    description="将二进制魔丸数据转换为GIF动画",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ququ85005702/NeZha2",
    author="ququ",
    author_email="85005702@qq.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=[],
    entry_points={}
)