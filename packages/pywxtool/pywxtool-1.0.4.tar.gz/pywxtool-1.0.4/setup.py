from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取版本号 pywxtool/__init__.py 中的 __version__
with open("pywxtool/__init__.py", "r", encoding="utf-8") as f:
    for line in f.readlines():
        if line.startswith("__version__"):
            version = line.split("=")[-1].strip().strip("\"'")
            break
    else:
        raise RuntimeError("version not found")

install_requires = [
    "setuptools>=42",  # 确保支持package_data
    "wheel"
]

setup(
    name="pywxtool",
    author="xaoyaoo",
    version=version,
    author_email="xaoyaoo@gmail.com",
    description="微信信息获取工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xaoyaoo",
    license='MIT',

    # packages=find_packages(exclude=[]),
    include_package_data=True,
    packages=find_packages(),
    package_dir={'pywxtool': 'pywxtool'},
    # include_package_data=True,
    package_data={
        'pywxtool': ["libs/*.dll"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8, <4',
    install_requires=install_requires,
    entry_points={
    },
    setup_requires=['wheel']
)
