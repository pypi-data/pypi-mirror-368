from setuptools import find_packages, setup


def readme():
    with open("README.md", "r") as f:
        return f.read()


base_requires = [
    "httpx>=0.28.1",
    "python-dotenv>=1.0.1",
]

langchain_requires = [
    "langchain-openai==0.2.5",
    "langchain-community==0.3.18",
    "langchain==0.3.19",
    "langchain_experimental==0.3.4",
]

crewai_requires = [
    "crewai>=0.95.0",
]

openai_agents_requires = [
    "openai-agents>=0.1.0",
]

setup(
    name="hivetrace",
    version="1.3.5",
    author="Raft",
    author_email="sales@raftds.com",
    description="Hivetrace SDK for monitoring LLM applications",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="http://hivetrace.ai",
    packages=find_packages(),
    install_requires=base_requires,
    extras_require={
        "base": base_requires,
        "langchain": langchain_requires,
        "crewai": crewai_requires,
        "openai_agents": openai_agents_requires,
        "all": base_requires
        + langchain_requires
        + crewai_requires
        + openai_agents_requires,
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="SDK, monitoring, logging, LLM, AI, Hivetrace",
    python_requires=">=3.8",
)
