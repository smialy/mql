.PHONY: test
test:
	pytest

.PHONY: testcov
testcov:
	pytest --cov=mql && (echo "building coverage html, view at './htmlcov/index.html'"; coverage html)
