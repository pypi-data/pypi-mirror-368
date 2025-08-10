from setuptools import setup

setup(
    name="rws",
    version="0.1.0",
    description="WebSocket client with Rust backend",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/rws",
    packages=["rws"],
    package_dir={"": "python"},
    package_data={
        "rws": ["py.typed"],
    },
    install_requires=[
        "typing-extensions>=4.0.0",
    ],
    python_requires=">=3.11",
) 