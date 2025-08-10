from setuptools import setup, find_packages

setup(
    name="vibeiseven",
    version="1.0.0",
    description="AI-powered even number detection using GPT or Gemini",
    author="Dean Billedo",
    author_email="deanreight@gmail.com",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "google-generativeai"
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
)
