from setuptools import setup, find_packages

setup(
    name="capsloves",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    author="Zalos",
    author_email="bza55losxsgytt@gmail.com",
    description="Client library for Captchasolver API",
    url="https://github.com/yourusername/capsloves",  # ضع رابط المشروع إذا كان موجودًا
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
