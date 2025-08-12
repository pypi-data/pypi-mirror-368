import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zmkj-rknn-tools",
    version="0.1.0",
    author="壹世朱名",
    author_email="nx740@qq.com",
    description="瑞芯微端侧的辅助快速验证工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuntee/rknn-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "zmkj-rknn-yolov8",
        "numpy",
        "opencv-python",
        "supervision",
        "rknn-toolkit2",
        "rknn-toolkit-lite2",
    ],
    keywords="rknn, rockchip, yolov8, object detection, edge computing",
)