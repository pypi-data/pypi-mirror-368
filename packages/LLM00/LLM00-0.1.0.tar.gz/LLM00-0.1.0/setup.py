
from setuptools import setup
# 公開用パッケージの作成 [ezpip]
import ezpip

# 公開用パッケージの作成 [ezpip]
with ezpip.packager(develop_dir = "./_develop_LLM00/") as p:
	setup(
		name = "LLM00",
		version = "0.1.0",
		description = 'An interface that allows you to use LLMs in an ultra-simple way',
		author = "bib_inf",
		author_email = "contact.bibinf@gmail.com",
		url = "https://github.co.jp/",
		packages = p.packages,
		install_requires = ["ezpip", "sout>=1.2.1", "relpath", "fies>=1.4.0"],
		long_description = p.long_description,
		long_description_content_type = "text/markdown",
		license = "CC0 v1.0",
		classifiers = [
			"Programming Language :: Python :: 3",
			"Topic :: Software Development :: Libraries",
			"License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication"
		],
		# entry_points = """
		# 	[console_scripts]
		# 	py6 = py6:console_command
		# """
	)
