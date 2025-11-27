# Evaluation of CoNLL-U import for UD-Swedish corpora

The following corpora are evaluated.

- [UD Swedish LinES](https://github.com/UniversalDependencies/UD_Swedish-LinES)
- [UD Swedish Old](https://github.com/UniversalDependencies/UD_Swedish-Old)
- [UD Swedish PUD](https://github.com/UniversalDependencies/UD_Swedish-PUD)
- [UD Swedish SweLL](https://github.com/UniversalDependencies/UD_Swedish-SweLL)
- [UD Swedish Talbanken](https://github.com/UniversalDependencies/UD_Swedish-Talbanken)

In these corpora there are:

- 48 [empty node] tokens
- 0 [multiword] tokens

The following files contains `empty nodes`:

| Filename                                            | Empty nodes |
| --------------------------------------------------- | ----------- |
| `UD_Swedish-PUD/sv_pud-ud-test.conllu`              | 9           |
| `UD_Swedish-Talbanken/sv_talbanken-ud-dev.conllu`   | 2           |
| `UD_Swedish-Talbanken/sv_talbanken-ud-test.conllu`  | 9           |
| `UD_Swedish-Talbanken/sv_talbanken-ud-train.conllu` | 28          |
| Total                                               | 48          |

The `empty nodes` are only used in advanced dependency relation (column `deps`).

[empty node]: https://universaldependencies.org/format.html#words-tokens-and-empty-nodes
[multiword]: https://universaldependencies.org/format.html#words-tokens-and-empty-nodes
