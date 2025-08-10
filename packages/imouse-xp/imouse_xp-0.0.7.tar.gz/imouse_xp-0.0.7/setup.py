from setuptools import setup, find_packages

setup(
    name="imouse_xp",  # 包名
    version="0.0.7",  # 版本号
    author="iMouse",
    author_email="your_email@example.com",
    description="iMouseXP版本的自动化控制的 Python 包",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iosauto/py-imouse",  # 你的 GitHub 地址
    packages=find_packages(),  # 自动查找 `iMouse` 目录下的 Python 包
    install_requires=[
        "annotated-types>=0.7.0",
        "certifi>=2024.12.14",
        "charset-normalizer>=3.4.1",
        "colorlog>=6.9.0",
        "idna>=3.10",
        "pydantic>=2.10.4",
        "pydantic_core>=2.27.2",
        "requests>=2.32.3",
        "typing_extensions>=4.12.2",
        "urllib3>=2.3.0",
        "websocket-client>=1.8.0",
        "annotated-types>=0.7.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
