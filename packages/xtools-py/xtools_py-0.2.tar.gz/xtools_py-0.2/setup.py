from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
   long_description = f.read()

setup(
	name="xtools-py",  # Имя пакета (уникальное на PyPI)
	version="0.2",  # Версия (следи за версионированием)
	author="Xpeawey",
	author_email="girectx@example.com",
	description="A set of useful utilities for Python developers",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/SikWeet/xtools",  # Ссылка на GitHub-репозиторий
	packages=find_packages(),  # Автоматический поиск пакетов
	install_requires=[
		"numpy",
	],
   include_package_data=True,
   python_requires=">=3.7",
   license="MIT",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
