.PHONY: test test-unit test-integration test-browser test-web api web

BACKEND=src/external-integrations/jobops-external-services
WEB=src/web/jobops-web

test: test-unit test-integration test-browser

test-unit:
	cd $(BACKEND) && PYTHONPATH=. pytest -q tests/unit

test-integration:
	cd $(BACKEND) && PYTHONPATH=. pytest -q tests/integration

test-browser:
	cd $(BACKEND) && PYTHONPATH=. pytest -q tests/browser

test-web:
	cd $(WEB) && npm run build

api:
	cd $(BACKEND) && PYTHONPATH=. python main.py

web:
	cd $(WEB) && npm run dev
