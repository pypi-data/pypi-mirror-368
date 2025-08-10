from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nexagen",
    version="1.0.1",
    author="Chongqing Taoxiang Network Technology Co., Ltd.",
    author_email="wei@taoxiang.org",
    description="Next-Generation Multi-Agent System Builder with MCP Protocol Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taoxiang-org/nexagen",
    license="MIT",  # 添加明确的许可证类型声明
    license_files="LICENSE",  # 改为字符串格式（重要修复！）
    project_urls={
        "Bug Reports": "https://github.com/taoxiang-org/nexagen/issues",
        "Source": "https://github.com/taoxiang-org/nexagen",
        "Documentation": "https://github.com/taoxiang-org/nexagen#readme",
        "Homepage": "https://www.taoxiang.org",
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nexagen=Nexagen.cli:cli",
        ],
    },
    package_data={
        "Nexagen": ["templates/*.j2"],
    },
    keywords="multi-agent, MCP, automation, AI, orchestration, agent-framework",
    zip_safe=False,
)