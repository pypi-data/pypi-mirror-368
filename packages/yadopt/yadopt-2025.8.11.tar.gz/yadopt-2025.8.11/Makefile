# Makefile

SOFTWARE = yadopt

help:
	@echo "Usage:"
	@echo "    make <command>"
	@echo ""
	@echo "Build commands:"
	@echo "    build         Build package"
	@echo "    testpypi      Upload package to TestPyPi"
	@echo "    pypi          Upload package to PyPi"
	@echo "    install-test  Install from TestPyPi"
	@echo ""
	@echo "Test and code check commands:"
	@echo "    check         Check the code quality"
	@echo "    count         Count the lines of code"
	@echo "    coverage      Measure code coverage"
	@echo "    test          Run test on this device"
	@echo "    testall       Run test on Docker"
	@echo ""
	@echo "Other commands:"
	@echo "    clean         Cleanup cache files"
	@echo "    help          Show this message"

check:
	pyflakes yadopt
	mypy yadopt
	pylint --max-line-length=120 yadopt

count:
	cloc --by-file yadopt/*.py

coverage:
	rm -rf .coverage
	coverage run --source yadopt tests/run_tests.py
	coverage html

test:
	python3 tests/run_tests.py

test-all:
	docker run --rm -it -v `pwd`:/work -w /work python:3.12 python3 tests/run_tests.py | tee /tmp/yadopt_test_py3_12.txt
	docker run --rm -it -v `pwd`:/work -w /work python:3.11 python3 tests/run_tests.py | tee /tmp/yadopt_test_py3_11.txt
	docker run --rm -it -v `pwd`:/work -w /work python:3.10 python3 tests/run_tests.py | tee /tmp/yadopt_test_py3_10.txt
	@echo ""
	@echo "----- Summary -----"
	@echo "Test on Python 3.12:" `cat /tmp/yadopt_test_py3_12.txt | tail -n 1`
	@echo "Test on Python 3.11:" `cat /tmp/yadopt_test_py3_11.txt | tail -n 1`
	@echo "Test on Python 3.10:" `cat /tmp/yadopt_test_py3_10.txt | tail -n 1`

build:
	python3 -m build

testpypi:
	twine upload --repository pypitest dist/*

pypi:
	twine upload --repository pypi dist/*

install-test:
	python3 -m pip install --index-url https://test.pypi.org/simple/ $(SOFTWARE)

clean:
	rm -rf dist .coverage .mypy_cache htmlcov `find -type d | grep __pycache__`

# vim: noexpandtab tabstop=4 shiftwidth=4
