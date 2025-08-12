from setuptools import setup

setup(
    install_requires=[
        "annotated-types>=0.7.0",
        "anyio>=4.10.0",
        "certifi>=2025.8.3",
        "exceptiongroup>=1.3.0",
        "h11>=0.16.0",
        "httpcore>=1.0.9",
        "httpx>=0.28.1",
        "idna>=3.10",
        "ollama>=0.5.3",
        "pydantic>=2.11.7",
        "pydantic_core>=2.33.2",
        "sniffio>=1.3.1",
        "tldr>=0.1",
        "tldrpy>=0.1",
        "typing-inspection>=0.4.1",
        "typing_extensions>=4.14.1",
    ],
    name='tldrcli',
    version='0.1.1',
    py_modules=['tldr'],
    author='Devanshu Pandya',
    author_email='pandyadevh@gmail.com',
    description='Your new CLI tool helping you learn and fix errors in Python fast!',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'tldr = tldr:main',
        ],
    },
)
