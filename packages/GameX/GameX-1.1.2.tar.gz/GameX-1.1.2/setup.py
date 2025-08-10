from setuptools import setup, find_packages
# python setup.py sdist
setup(
    name="GameX",
    version="1.1.2",
    packages=find_packages(),
    include_package_data=True,  # 必须启用资源包含
    description=(
        "Welcome to GameX, a product developed using Pygame! "
        "It is more suitable for people have just switched from "
        "Scratch to Python. This lib is simple and easy to use."
    ),
    package_data={
        'GameX': [
            # 1. 包含所有Python文件
            '*.py',
            # 2. 精确匹配字体文件（根据图片路径）
            'data/fonts/*.ttf',   # TTF格式
            # 3. 精确匹配图片文件（根据图片路径）
            'data/images/*.jpg',
            # 4. 三级递归通配符（军工级保障）
            'data/*',        # 包含data目录下所有文件
            'data/*/*',      # 包含data下所有子目录的文件
            'data/*/*/*'     # 包含data下所有三级子目录的文件
        ]
    },
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown"
)