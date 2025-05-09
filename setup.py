from setuptools import setup, find_packages

setup(
    name="origyn",
    version="0.1.0",
    description="A tool to identify Original Equipment Manufacturers (OEM) and UNSPSC Categorization for spare parts from the material procurement datasets.",
    author="Tushar Nair",
    author_email="tushar_nair@outlook.com",
    url="https://github.com/TusharNair04/origyn",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
        "langchain-core>=0.1.0",
        "groq>=0.4.0",
        "google-cloud-translate>=3.8.0",
        "langgraph>=0.0.15",
        "sentence-transformers>=2.2.0",
        "chromadb>=0.4.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8"
)