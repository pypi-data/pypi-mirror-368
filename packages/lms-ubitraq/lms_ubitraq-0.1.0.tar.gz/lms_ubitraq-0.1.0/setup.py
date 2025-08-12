from setuptools import setup, find_packages

setup(
    name="lms-ubitraq",
    version="0.1.0",
    author="MrYuGoui",
    author_email="MrYuGoui@163.com",
    description="LMS的全迹解算引擎对接驱动",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mryugoui/django_plugin_ubitraq",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'lms_ubitraq': [
            'templates/*/*.html',  # 递归包含
            'static/*/*.*',
        ]
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Django",
        "numpy",
        "djangorestframework",
        "django-object-actions",
        "drf-spectacular",
        "requests",
        "websocket-client",
        "lms-geotool",
        "django-import-export",
    ],
)
