import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ats_case",
    version="2.1.81",
    py_modules=['ats_case'],
    author="zhangyue",
    author_email="zhangyue@techen.cn",
    description="Test Script Development Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/henry9000/ats_case",
    project_urls={
        "Bug Tracker": "https://gitee.com/henry9000/ats_case/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    install_requires=["pytest", "pytest-ordering", "psutil", "gevent", "ats-base"],
    package_data={
        '': ['*.tmp'],
    },
)
