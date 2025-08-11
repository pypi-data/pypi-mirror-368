from setuptools import setup, find_packages

setup(
    name="microsoft-teams-mcp",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "fastmcp==2.11.2",
        "requests==2.32.4",
        "httpx==0.28.1",
        "python-dateutil==2.9.0.post0",
        "pytz==2025.2",
        "msgraph-core==1.3.5",
        "azure-identity==1.24.0",
        "python-dotenv==1.1.1",
        "msgraph-sdk==1.40.0",
    ],
    author="Naveen Chowdary Aliveli",
    author_email="naveenchowdary5175@gmail.com",
    description="Microsoft Teams meeting scheduler MCP tool using Microsoft Graph API",
    url="https://github.com/alivnavc/Microsoft-Teams-Meetings-MCP-Server",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "teams-mcp-server=microsoft_teams_mcp.server:main"
        ]
    }
)