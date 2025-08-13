from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tavily-mcp-server",
    version="1.0.0",
    description="Tavily搜索MCP服务智能体 - 为AI智能体提供强大的网络搜索能力",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MCP Team",
    author_email="support@mcp.dev",
    url="https://github.com/mcp-team/tavily-mcp-server",
    project_urls={
        "Bug Tracker": "https://github.com/mcp-team/tavily-mcp-server/issues",
        "Documentation": "https://github.com/mcp-team/tavily-mcp-server#readme",
        "Source Code": "https://github.com/mcp-team/tavily-mcp-server",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'tavily-mcp=tavily_mcp_server.server:main',
        ],
    },
    python_requires=">=3.8",
    keywords=["tavily", "search", "mcp", "ai", "agent", "fastapi", "web-search"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: FastAPI",
    ],
    license="MIT",
)