import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ats_base",
    version="1.3.4",
    py_modules=['ats_base'],
    author="zhangyue",
    author_email="zhangyue@techen.cn",
    description="Test Script Development Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/henry9000/ats_base",
    project_urls={
        "Bug Tracker": "https://gitee.com/henry9000/ats_base/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    install_requires=["python-dateutil", "requests", "colorlog"],
    package_data={
        'ats_base.config': ['config.ini'],
    },
)
