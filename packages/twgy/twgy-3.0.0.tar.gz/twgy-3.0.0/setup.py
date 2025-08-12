#!/usr/bin/env python3
"""
TWGY - Taiwan Mandarin Phonetic Similarity Processor
語音相似性處理系統，專門針對台灣國語語音變異優化
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# 讀取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 讀取requirements.txt
def read_requirements():
    requirements = []
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    except FileNotFoundError:
        # 基本依賴
        requirements = [
            'numpy>=1.20.0',
            'pandas>=1.3.0',
            'pypinyin>=0.44.0',
            'dimsim>=0.2.0',
            'tqdm>=4.60.0',
            'scikit-learn>=1.0.0',
            'requests>=2.25.0'
        ]
    return requirements

setup(
    name="twgy",
    version="3.0.0",
    author="TWGY Development Team",
    author_email="twgy.dev@example.com",
    description="Taiwan Mandarin Phonetic Similarity Processor - 台灣國語語音相似性處理系統",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/twgy",
    
    packages=find_packages(),
    
    # 包含數據文件
    include_package_data=True,
    package_data={
        'twgy': [
            'data/super_dicts/*.json',
            'data/phonetic_data/*.json',
            'data/training_logs/*.json',
        ],
    },
    
    # 依賴
    install_requires=read_requirements(),
    
    # 可選依賴
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.812',
            'jupyter>=1.0'
        ],
        'full': [
            'sentence-transformers>=2.0',
            'faiss-cpu>=1.7.0',
            'torch>=1.9.0',
        ],
        'api': [
            'fastapi>=0.68.0',
            'uvicorn>=0.15.0',
            'pydantic>=1.8.0',
        ]
    },
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 分類標籤
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Traditional)",
        "Natural Language :: Chinese (Simplified)",
    ],
    
    # 關鍵詞
    keywords="chinese mandarin phonetic similarity asr nlp taiwan linguistics",
    
    # 命令行工具
    entry_points={
        'console_scripts': [
            'twgy=twgy.cli:main',
            'twgy-test=twgy.testing:run_tests',
            'twgy-benchmark=twgy.benchmark:run_benchmark',
        ],
    },
    
    # 項目URL
    project_urls={
        "Bug Reports": "https://github.com/yourusername/twgy/issues",
        "Source": "https://github.com/yourusername/twgy",
        "Documentation": "https://twgy.readthedocs.io/",
        "Changelog": "https://github.com/yourusername/twgy/blob/main/CHANGELOG.md",
    },
)