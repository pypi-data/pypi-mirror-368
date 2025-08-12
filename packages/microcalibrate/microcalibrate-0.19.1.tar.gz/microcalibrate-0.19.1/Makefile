

test:
	pytest tests/ --cov=microcalibrate --cov-report=xml --maxfail=0 -v

install:
	pip install -e ".[dev]"

check-format:
	linecheck .
	isort --check-only --profile black src/
	black . -l 79 --check

format:
	linecheck . --fix
	isort --profile black src/
	black . -l 79

documentation:
	cd docs && jupyter-book build .
	python docs/add_plotly_to_book.py docs/_build/html

build:
	pip install build
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info/
	rm -rf docs/_build/

changelog:
	build-changelog changelog.yaml --output changelog.yaml --update-last-date --start-from 0.1.0 --append-file changelog_entry.yaml
	build-changelog changelog.yaml --org PolicyEngine --repo microcalibrate --output CHANGELOG.md --template .github/changelog_template.md
	bump-version changelog.yaml pyproject.toml
	rm changelog_entry.yaml || true
	touch changelog_entry.yaml

dashboard-install:
	cd microcalibration-dashboard && npm install

dashboard-dev:
	cd microcalibration-dashboard && npm run dev

dashboard-build:
	cd microcalibration-dashboard && npm run build

dashboard-start:
	cd microcalibration-dashboard && npm start

dashboard-clean:
	cd microcalibration-dashboard && rm -rf .next node_modules

dashboard-static:
	cd microcalibration-dashboard && npm run static

dashboard-preview:
	cd microcalibration-dashboard && npm run static && npx serve out

dashboard-check:
	cd microcalibration-dashboard && npm run lint && npm run static && echo "✅ Dashboard ready for GitHub Pages deployment"
