.PHONY: test demo lint clean

test:
	python -m unittest discover -s tests -q

demo:
	rm -rf .demo && python -m githood new examples/momentum.spec.md -o .demo && \
	cd .demo && python -m unittest discover -s tests -q

lint:
	python -m compileall -q githood tests

clean:
	rm -rf .demo build dist *.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
