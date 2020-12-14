from setuptools import setup, find_packages

setup(
    name="tod0",
    version="0.6.1",
    author="kiblee",
    author_email="kiblee@pm.me",
    packages=find_packages(),
    url="https://github.com/kiblee/tod0",
    license="LICENSE",
    description="A Terminal Client for Microsoft To-Do.",
    install_requires=[
        "prompt-toolkit",
        "pyyaml",
        "requests",
        "requests_oauthlib",
        "tzlocal",
    ],
    include_package_data=True,
    entry_points="""
        [console_scripts]
        tod0=todocli.interface:run
        todocli=todocli.cli:main
    """,
    python_requires=">=3.6",
)
