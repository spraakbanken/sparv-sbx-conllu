# sparv-sbx-conllu

[![PyPI version](https://img.shields.io/pypi/v/sparv-sbx-conllu.svg)](https://pypi.org/project/sparv-sbx-conllu/)
[![PyPI license](https://img.shields.io/pypi/l/sparv-sbx-conllu.svg)](https://pypi.org/project/sparv-sbx-conllu/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sparv-sbx-conllu.svg)](https://pypi.org/project/sparv-sbx-conllu)

[![Maturity badge - level 2](https://img.shields.io/badge/Maturity-Level%202%20--%20First%20Release-yellowgreen.svg)](https://github.com/spraakbanken/getting-started/blob/main/scorecard.md)
[![Stage](https://img.shields.io/pypi/status/sparv-sbx-conllu.svg)](https://pypi.org/project/sparv-sbx-conllu/)

[![codecov](https://codecov.io/gh/spraakbanken/sparv-sbx-conllu/graph/badge.svg?token=DUV4CL6AK2)](https://codecov.io/gh/spraakbanken/sparv-sbx-conllu)

[![CI(check)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/check.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/check.yml)
[![CI(release)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/release.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/release.yml)
[![CI(scheduled)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/rolling.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/rolling.yml)
[![CI(test)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/test.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-conllu/actions/workflows/test.yml)

[sparv]: https://github.com/spraakbanken/sparv

Plugin to [sparv] import `CoNLL-U` files to Sparv.

## Install

First, install [sparv] as suggested,

```bash
pipx install sparv
```

Then install `sparv-sbx-conllu` with

```bash
sparv plugins install sparv-sbx-conllu
```

## Usage

To use this plugin to import CoNLL-U files to your corpus, add the following to your `config.yaml`:

```yaml
# file=config.yaml
import:
  importer: sbx_conllu:parse
```

### Configuration

All annotations are exported by default, but if you want to use a annotation in another analysis
you need to specify them in your `config.yaml`.

By default, `sparv_sbx_conllu` exports the annotations `text`, `document`, `sentence`and `token`.
Other annotations can be added to `sbx_conllu.import_attributes`.

For instance, to use the annotations `token:xpos` and `sentence:sent_id` add them like this:

```yaml
# file=config.yaml
sbx_conllu:
  import_attributes:
    - token:xpos
    - sentence:sent_id
```

#### Classes

To use annotations from `sparv_sbx_conllu` in other analysis you can be needed to add them to `classes`
in your `config.yaml`.

##### Example

You want to use the `sentence` and `token` from `sparv_sbx_conllu` and also map `token:xpos` as `token:pos` and `token:pos_ud` as `token:upos`.

```yaml
# file=config.yaml
classes:
  sentence: sentence
  token: token
  "token:pos": token:xpos
  "token:upos": token:pos_ud
```

##### Common annotation from a standard CoNLL-U file

These annotations are some of the annotations you can expect from a CoNLL-U file, but it depends on the file.

| Annotation         | CoNLL-U column                              | Always?                                                | Comment                                            | Example in CoNLL-U                           |
| ------------------ | ------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------- | -------------------------------------------- | ---------- | ----------- | ------------- |
| `text`             |                                             | yes                                                    | the whole text                                     |
| `document`         |                                             | yes                                                    | either implicit, or at least one specified         |
| `sentence`         |                                             | yes                                                    | must contain at least one sentence                 |
| `token`            |                                             | yes                                                    | must contain at least one token                    |
| `document:id`      | `# newdoc id =`                             | no                                                     |                                                    | `# newdoc id = ID` gives `document:id = ID`  |
| `paragraph`        | `# newpar`<br>`NewPar=Yes` in column `misc` | no                                                     | Can exist around sentences<br>And inside sentences | `# newpar`<br>`NewPar=Yes` in `misc` column  |
| `paragraph:id`     | `# newpar id =`                             | no                                                     |                                                    | `# newpar id = ID` gives `paragraph:id = ID` |
| `token:id`         | `id` column                                 | no                                                     | Always present in standard CoNLL-U                 |
| `form` column      | no                                          | Always present in standard CoNLL-U, may contain spaces |
| `token:baseform`   | `lemma` column                              | no                                                     | May contain spaces                                 |
| `token:pos_ud`     | `upos` column                               | no                                                     | UD POS                                             |
| `token:xpos`       | `xpos` column                               | no                                                     | custom POS (no standard)                           |
| `token:feats_ud`   | `feats` column                              | no                                                     | Dict-like values                                   | `Case=Nom                                    | Gender=Fem | Number=Sing | Polarity=Pos` |
| `token:dephead_ud` | `head` column                               | no                                                     | integer                                            |
| `token:deprel_ud`  | `deprel` column                             | no                                                     | UD-dep value                                       |
| `token:deps_ud     | `deps` column                               | no                                                     | At least one pair `head`:`deprel`                  | `2:obj                                       | 4:obj`     |
| `token:misc_ud`    | `misc` column                               | no                                                     | Dict-like values                                   | `SpaceAfter=No`                              |

## Known issues

### Importing CoNLL-U

Sparv will log a warning if any of the following are encountered.

- When importing CoNLL-U data, empty nodes are skipped. E.g. `id = 5.1` [Tracking issue](https://github.com/spraakbanken/sparv-sbx-conllu/issues/14)
- When importing CoNLL-U data, tokens inside multiword tokens are skipped.
  E.g. `id = 2-3` are added, but `id = 2` and `id = 3` are skipped. [Tracking issue](https://github.com/spraakbanken/sparv-sbx-conllu/issues/15)

## Minimum Supported Python Version Policy

The Minimum Supported Python Version is fixed for a given minor (1.x)
version. However it can be increased when bumping minor versions, i.e. going
from 1.0 to 1.1 allows us to increase the Minimum Supported Python Version. Users unable to increase their
Python version can use an older minor version instead. Below is a list of sparv-sbx-conllu versions
and their Minimum Supported Python Version:

- v0.1: Python 3.11.

Note however that sparv-sbx-conllu also has dependencies, which might have different MSPV
policies. We try to stick to the above policy when updating dependencies, but
this is not always possible.

## Changelog

This project keeps a [changelog](./CHANGELOG.md).

## License

This repository is licensed under the [MIT](./LICENSE) license.

## Development

### Development prerequisites

- [`uv`](https://docs.astral.sh/uv/)
- [`pre-commit`](https://pre-commit.org)

For starting to develop on this repository:

- Clone the repo (in one of the ways below):
  - `git clone git@github.com:spraakbanken/sparv-sbx-conllu.git`
  - `git clone https://github.com/spraakbanken/sparv-sbx-conllu.git`
- Setup environment: `make dev`
- Install `pre-commit` hooks: `pre-commit install`

Do your work.

Tasks to do:

- Test the code with `make test` or `make test-w-coverage`.
  - Snapshot can be updated by `make snapshot-update`
- Lint the code with `make lint`.
- Check formatting with `make check-fmt`.
- Format the code with `make fmt`.
- Type-check the code with `make type-check`.
- Test the examples with:
  - `make test-example-en_ewt-ud-test`
  - `make test-example-long-token-to-text`
  - `make test-example-no-metadata`
  - `make test-example-paragraph-and-document`
  - `make test-example-paragraph-in-sentence`
  - `make test-example-sentence-comments`

This repo uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Release a new version

- Prepare the CHANGELOG: `make prepare-release`.
- Edit `CHANGELOG.md` to your liking.
- Add to git: `git add --update`
- Commit with `git commit -m 'chore(release): prepare release'` or `cog commit chore 'prepare release' release`.
- Bump version (depends on [`bump-my-version](https://callowayproject.github.io/bump-my-version/))
  - install with `uv tool install bump-my-version`
  - Major: `make bumpversion part=major`
  - Minor: `make bumpversion part=minor`
  - Patch: `make bumpversion part=patch` or `make bumpversion`
- Push `main` and tags to GitHub: `git push main --tags` or `make publish`
  - [GitHub Actions workflow](./.github/workflows/release.yaml) will build, test and publish the package to [PyPi](https://pypi.prg).
- Add metadata for [Språkbanken's resource](https://spraakbanken.gu.se/analyser)
  - Generate metadata: `make generate-metadata`
  - Upload the files from `assets/metadata/export/sbx_metadata/analysis` to <https://github.com/spraakbanken/metadata/tree/main/yaml/analysis>.
