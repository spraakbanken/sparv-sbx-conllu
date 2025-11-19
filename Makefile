
# use this Makefile as base in your project by running
# git remote add make https://github.com/spraakbanken/python-uv-make-conf
# git fetch make
# git merge --allow-unrelated-histories make/main
#
# To later update this makefile:
# git fetch make
# git merge make/main
#
.default: help

.PHONY: help
help:
	@echo "usage:"
	@echo "dev | install-dev"
	@echo "   setup development environment"
	@echo "install"
	@echo "   setup production environment"
	@echo ""
	@echo "info"
	@echo "   print info about the system and project"
	@echo ""
	@echo "test"
	@echo "   run all tests"
	@echo ""
	@echo "test-w-coverage [cov=] [cov_report=]"
	@echo "   run all tests with coverage collection. (Default: cov_report='term-missing', cov='--cov=${PROJECT_SRC}')"
	@echo ""
	@echo "lint"
	@echo "   lint the code"
	@echo ""
	@echo "lint-fix"
	@echo "   lint the code and try to fix it"
	@echo ""
	@echo "type-check"
	@echo "   check types"
	@echo ""
	@echo "fmt"
	@echo "   format the code"
	@echo ""
	@echo "check-fmt"
	@echo "   check that the code is formatted"
	@echo ""
	@echo "bumpversion [part=]"
	@echo "   bumps the given part of the version of the project. (Default: part='patch')"
	@echo ""
	@echo "bumpversion-show"
	@echo "   shows the bump path that is possible"
	@echo ""
	@echo "publish [branch=]"
	@echo "   pushes the given branch including tags to origin, for CI to publish based on tags. (Default: branch='main')"
	@echo "   Typically used after 'make bumpversion'"
	@echo ""
	@echo "prepare-release"
	@echo "   run tasks to prepare a release"
	@echo ""

PLATFORM := `uname -o`
REPO := spraakbanken/sparv-sbx-conllu
PROJECT_SRC := src/sbx_conllu

ifeq (${VIRTUAL_ENV},)
  VENV_NAME = .venv
  INVENV = uv run
else
  VENV_NAME = ${VIRTUAL_ENV}
  INVENV =
endif

ifeq (${CI},)
  DIFF = difft --exit-code
else
  DIFF = diff
endif

default_cov := "--cov=${PROJECT_SRC}"
cov_report := "term-missing"
cov := ${default_cov}

all_tests := tests
tests := tests

info:
	@echo "Platform: ${PLATFORM}"
	@echo "INVENV: '${INVENV}'"

dev: install-dev

# setup development environment
install-dev: install-pre-commit
	uv sync --all-packages --dev

# install pre-commit hooks
install-pre-commit: .git/hooks/pre-commit
.git/hooks/pre-commit: .pre-commit-config.yaml
	@if command -v pre-commit > /dev/null; then pre-commit install; else echo "WARN: 'pre-commit' not installed"; fi

# setup production environment
install:
	uv sync --all-packages --no-dev

lock: uv.lock

uv.lock: pyproject.toml
	uv lock

.PHONY: test
test:
	${INVENV} pytest -vv ${tests}

.PHONY: test-w-coverage
# run all tests with coverage collection
test-w-coverage:
	${INVENV} pytest -vv ${cov} --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=lcov:coverage.lcov ${all_tests}

.PHONY: doc-tests
doc-tests:
	${INVENV} pytest ${cov} --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=lcov:coverage.lcov --doctest-modules ${PROJECT_SRC}

.PHONY: type-check
# check types
type-check:
	${INVENV} mypy ${PROJECT_SRC} ${tests}

.PHONY: lint
# lint the code
lint:
	${INVENV} ruff check ${PROJECT_SRC} ${tests}

.PHONY: lint-fix
# lint the code (and fix if possible)
lint-fix:
	${INVENV} ruff check --fix ${PROJECT_SRC} ${tests}

part := "patch"
bumpversion:
	${INVENV} bump-my-version bump ${part}

bumpversion-show:
	${INVENV} bump-my-version show-bump

# run formatter(s)
fmt:
	${INVENV} ruff format ${PROJECT_SRC} ${tests}

.PHONY: check-fmt
# check formatting
check-fmt:
	${INVENV} ruff format --check ${PROJECT_SRC} ${tests}

build:
	uv build

branch := "main"
publish:
	git push -u origin ${branch} --tags


.PHONY: prepare-release
prepare-release: update-changelog tests/requirements-testing.lock

# we use lock extension so that dependabot doesn't pick up changes in this file
tests/requirements-testing.lock: pyproject.toml
	uv export --dev --format requirements-txt --no-hashes --no-emit-project --output-file $@

.PHONY: update-changelog
update-changelog: CHANGELOG.md

.PHONY: CHANGELOG.md
CHANGELOG.md:
	git cliff --unreleased --prepend $@

# update snapshots for `syrupy`
.PHONY: snapshot-update
snapshot-update:
	${INVENV} pytest --snapshot-update

### === project targets below this line ===
test-example-long-token-to-text:
	rm -rf examples/long-token-to-text/export examples/long-token-to-text/sparv-workdir examples/long-token-to-text/.snakemake
	cd examples/long-token-to-text; ${INVENV} sparv run --stats --log-to-file debug
	${DIFF} assets/long-token-to-text/long-token-to-text_export.gold.xml \
	    examples/long-token-to-text/export/xml_export.pretty/long-token-to-text_export.xml
	${DIFF} assets/long-token-to-text/preserved_format/long-token-to-text_export.gold.xml \
	    examples/long-token-to-text/export/xml_export.preserved_format/long-token-to-text_export.xml

snapshot-update-example-long-token-to-text: \
	assets/long-token-to-text/long-token-to-text_export.gold.xml \
	assets/long-token-to-text/preserved_format/long-token-to-text_export.gold.xml

assets/long-token-to-text/long-token-to-text_export.gold.xml: \
		examples/long-token-to-text/export/xml_export.pretty/long-token-to-text_export.xml
	@cp "$<" "$@"

assets/long-token-to-text/preserved_format/long-token-to-text_export.gold.xml: \
	 examples/long-token-to-text/export/xml_export.preserved_format/long-token-to-text_export.xml
	@cp "$<" "$@"

test-example-no-metadata:
	rm -rf examples/no-metadata/export examples/no-metadata/sparv-workdir examples/no-metadata/.snakemake
	cd examples/no-metadata; ${INVENV} sparv run --stats --log-to-file debug
	${DIFF} assets/no-metadata/preserved_format/empty-node_export.gold.xml \
	    examples/no-metadata/export/xml_export.preserved_format/empty-node_export.xml
	${DIFF} assets/no-metadata/preserved_format/multiword_export.gold.xml \
	    examples/no-metadata/export/xml_export.preserved_format/multiword_export.xml
	${DIFF} assets/no-metadata/preserved_format/space-after-no_export.gold.xml \
	    examples/no-metadata/export/xml_export.preserved_format/space-after-no_export.xml

snapshot-update-example-no-metadata: \
	assets/no-metadata/preserved_format/empty-node_export.gold.xml \
	assets/no-metadata/preserved_format/multiword_export.gold.xml \
	assets/no-metadata/preserved_format/space-after-no_export.gold.xml

assets/no-metadata/preserved_format/empty-node_export.gold.xml: \
	    examples/no-metadata/export/xml_export.preserved_format/empty-node_export.xml
	@cp "$<" "$@"

assets/no-metadata/preserved_format/multiword_export.gold.xml: \
    examples/no-metadata/export/xml_export.preserved_format/multiword_export.xml
	@cp "$<" "$@"

assets/no-metadata/preserved_format/space-after-no_export.gold.xml: \
	    examples/no-metadata/export/xml_export.preserved_format/space-after-no_export.xml
	@cp "$<" "$@"

test-example-paragraph-and-document:
	rm -rf examples/paragraph-and-document/export examples/paragraph-and-document/sparv-workdir examples/paragraph-and-document/.snakemake
	cd examples/paragraph-and-document; ${INVENV} sparv run --stats --log-to-file debug
	${DIFF} assets/paragraph-and-document/paragraph-and-document_export.gold.xml \
	examples/paragraph-and-document/export/xml_export.pretty/paragraph-and-document_export.xml

snapshot-update-example-paragraph-and-document: \
	assets/paragraph-and-document/paragraph-and-document_export.gold.xml

assets/paragraph-and-document/paragraph-and-document_export.gold.xml: \
		examples/paragraph-and-document/export/xml_export.pretty/paragraph-and-document_export.xml
	@cp "$<" "$@"

test-example-en_ewt-ud-test:
	rm -rf examples/en_ewt-ud-test/export examples/en_ewt-ud-test/sparv-workdir examples/en_ewt-ud-test/.snakemake
	cd examples/en_ewt-ud-test; ${INVENV} sparv run --stats --log-to-file debug
	${DIFF} assets/en_ewt-ud-test/en_ewt-ud-test_excerp_export.gold.xml \
	examples/en_ewt-ud-test/export/xml_export.pretty/en_ewt-ud-test_excerp_export.xml

snapshot-update-example-en_ewt-ud-test: \
	assets/en_ewt-ud-test/en_ewt-ud-test_excerp_export.gold.xml

assets/en_ewt-ud-test/en_ewt-ud-test_excerp_export.gold.xml: \
		examples/en_ewt-ud-test/export/xml_export.pretty/en_ewt-ud-test_excerp_export.xml
	@cp "$<" "$@"

test-example-paragraph-in-sentence:
	rm -rf examples/paragraph-in-sentence/export examples/paragraph-in-sentence/sparv-workdir examples/paragraph-in-sentence/.snakemake
	cd examples/paragraph-in-sentence; ${INVENV} sparv run --stats --log-to-file debug
	${DIFF} assets/paragraph-in-sentence/paragraph-in-sentence_export.gold.xml \
	examples/paragraph-in-sentence/export/xml_export.pretty/paragraph-in-sentence_export.xml

snapshot-update-example-paragraph-in-sentence: \
	assets/paragraph-in-sentence/paragraph-in-sentence_export.gold.xml

assets/paragraph-in-sentence/paragraph-in-sentence_export.gold.xml: \
		examples/paragraph-in-sentence/export/xml_export.pretty/paragraph-in-sentence_export.xml
	@cp "$<" "$@"
