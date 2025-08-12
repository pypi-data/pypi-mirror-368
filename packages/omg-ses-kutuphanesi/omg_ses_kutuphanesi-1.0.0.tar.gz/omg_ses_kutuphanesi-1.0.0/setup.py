from setuptools import setup, find_packages

setup(
    name="omg_ses_kutuphanesi",
    version="1.0.0",
    packages=find_packages(),
    description="Basit ses çalma kütüphanesi",
    author="Recep",
    author_email="seninmailin@gmail.com",
    url="https://github.com/kullanici/omg_ses_kutuphanesi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={"omg_ses_kutuphanesi": ["ses.wav"]},
    install_requires=[
        "pygame>=2.0.0",   # Buraya ekledim
    ],
)

