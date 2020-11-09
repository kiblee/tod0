import setuptools

setuptools.setup(
    name="tod0",
    version="0.5.0",
    author="kiblee",
    author_email="kiblee@pm.me",
    packages=["todocli", "todocli.test"],
    url="https://github.com/kiblee/tod0",
    license="LICENSE",
    description="A Terminal Client for Microsoft To-Do.",
    install_requires=["prompt-toolkit", "pyyaml", "requests", "requests_oauthlib",],
    include_package_data=True,
    entry_points="""
        [console_scripts]
        tod0=todocli.interface:run
    """,
    python_requires=">=3.6",
)
