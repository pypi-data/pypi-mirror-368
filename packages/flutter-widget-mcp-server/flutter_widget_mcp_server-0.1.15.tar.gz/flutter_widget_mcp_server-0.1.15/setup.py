from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="flutter_widget_mcp_server",
    version="0.1.15",
    author="anquan9494",
    author_email="anquan9494@gmail.com",
    description="Flutter Widget MCP Server for YL AI-enhanced Flutter component library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flutter_widget_mcp_server=flutter_widget_mcp_server.main:pypi_run"
        ]
    },
    package_data={
        "flutter_widget_mcp_server": ["components.json"],
    },
)
