from setuptools import setup, find_packages

setup(
    name="gmaps-image-fetcher",
    version="0.3.2",
    description="Stitch together Google Maps images from lat, long coordinates using the Static Maps API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/joseph-holland/gmaps-image-fetcher",
    packages=find_packages(),
    python_requires=">=3.5",
    install_requires=[
        "requests>=2.22.0",
        "Pillow>=6.0.0"
    ],
    entry_points={
        "console_scripts": [
            "gmaps-image-fetcher=gmaps_image_fetcher.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
