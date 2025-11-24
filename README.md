# sparv-sbx-conllu

## Known issues

### Importing CoNLL-U

Sparv will log a warning if any of the following are encountered.

- When importing CoNLL-U data, empty nodes are skipped. [Tracking issue](https://github.com/spraakbanken/sparv-sbx-conllu/issues/14)
- When importing CoNLL-U data, tokens inside multiword tokens are skipped. [Tracking issue](https://github.com/spraakbanken/sparv-sbx-conllu/issues/15)
