test:
	echo "TODO"
	#	nosetests --with-coverage --cover-package=megalus --cover-min-percentage=85
	#	pydocstyle megalus/
	#	pycodestyle --max-line-length=120 --exclude=megalus/tests/__init__.py megalus/
	#	mypy -p megalus --ignore-missing-imports --no-implicit-optional --no-strict-optional
changelog:
	echo "TODO"
release:
	echo "TODO"
deploy:
	rm -rf dist/
	python setup.py sdist bdist_wheel
	twine upload dist/*
