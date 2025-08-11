import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="extract_video_frame",
    version="1.0.2",
    author="ilpanda",
    author_email="litencent@gmail.com",
    description="extract video frame to tmp folder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "opencv-python",
    ],
    entry_points={
        "console_scripts": [
            "extract_video_frame=extract_video_frame.core:main",
        ],
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
