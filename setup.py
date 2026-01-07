from setuptools import setup, find_packages

setup(
    name="freq-ai-vertex",
    version="0.1.0",
    description="FREQ AI Sophisticated Operational Lattice - Natural language orchestration on Vertex AI",
    author="DRE Orchestrator AI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "google-cloud-aiplatform>=1.38.0",
        "google-cloud-bigquery>=3.11.0",
        "google-auth>=2.23.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
        "python-statemachine>=2.1.0",
        "structlog>=23.2.0",
        "python-json-logger>=2.0.7",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
