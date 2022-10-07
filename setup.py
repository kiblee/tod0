from setuptools import setup, find_packages

exec(open("todocli/__init__.py").read())

setup(
    name="tod0",
    version=__version__,
    author="kiblee",
    author_email="kiblee@pm.me",
    packages=find_packages(),
    url="https://github.com/kiblee/tod0",
    license="LICENSE",
    description="A Terminal Client for Microsoft To-Do.",
    install_requires=[
        "prompt-toolkit>=3.0.31",
        "pyyaml",
        "requests>=2.28.1",
        "requests_oauthlib",
        "bs4",
        "yaspin>=2.2.0",
    ],
    include_package_data=True,
    entry_points="""
        [console_scripts]
        tod0=todocli.interface:run
        todocli=todocli.cli:main
    """,
    python_requires=">=3.6",
)
