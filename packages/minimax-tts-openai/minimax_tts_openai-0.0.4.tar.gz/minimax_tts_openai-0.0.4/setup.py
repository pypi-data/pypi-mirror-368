from setuptools import setup, find_packages
import os

# Read README.md for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A proxy service converts Minimax TTS API to OpenAI-compatible format"

from setuptools import setup, find_packages
import os

# Read README.md for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A proxy service converts Minimax TTS API to OpenAI-compatible format"

# Read requirements.txt for install requirements
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "fastapi",
        "uvicorn",
        "requests",
        "pydantic",
        "PyYAML"
    ]

setup(
    name="minimax-tts-openai",
    version="0.0.4",
    author="Moha-Master",
    author_email="hongkongreporter@outlook.com",
    description="A proxy service converts Minimax TTS API to OpenAI-compatible format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Moha-Master/MiniMax-TTS-OpenAI",
    packages=find_packages(),
    py_modules=[
        "minimax_tts_openai.__main__",
        "minimax_tts_openai.app",
        "minimax_tts_openai.config"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "minimax-tts-openai=minimax_tts_openai.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "minimax_tts_openai": ["config.yaml.example"],
    },
)
