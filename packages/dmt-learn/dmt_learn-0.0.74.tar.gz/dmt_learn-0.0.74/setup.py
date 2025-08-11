from setuptools import setup, find_packages

setup(
    name="dmt_learn",
    version="0.0.74",  
    author="Zelin Zang",  
    author_email="zangzelin@westlake.edu.cn",
    description="dmt learn package", 
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # README 的格式
    url="https://github.com/yourusername/my_package",  # 项目主页
    packages=find_packages(),  # 自动查找所有包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # 支持的 Python 版本
    install_requires=[
        # 在此列出依赖项，例如：``
        "numpy>=1.21.0",
        "plotly",
        "scikit-learn",
        "pandas",
        "lightning",
        "wandb",
        "munkres",
        "umap-learn",
        "scanpy",
        "kaleido",
        "transformers",
    ],
)