from setuptools import setup, find_packages

setup(
    name="genai_colosseum_premium",
    version="0.2.3",
    packages=find_packages(),
    include_package_data=True,
    package_data={
    'genai_colosseum_premium': ['templates/*'],
},
    install_requires=["click", "requests"],
    entry_points={
        "console_scripts": [
            "genai-premium=genai_colosseum_premium.cli:cli"
        ]
    }
)
