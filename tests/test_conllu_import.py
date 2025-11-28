from pathlib import Path
from unittest import mock

import conllu
import pytest
from sparv.api import Output, Source, SourceFilename, SourceStructure, Text
from syrupy.assertion import SnapshotAssertion

from sbx_conllu.conllu_import import SparvCoNLLUParser, _find_root, analyze_conllu, parse  # noqa: PLC2701

# id   form  lemma upostag xpostag           feats  head    deprel deps  misc
EXAMPLE_NO_TEXT: str = """
1    The    the     DET      DT               _     5       det    _   _
2  quick  quick     ADJ      JJ      Degree=pos     5      amod    _   _
3  brown  brown     ADJ      JJ      Degree=pos     5      amod    _   _
4    fox    fox    NOUN      NN     Number=sing     5  compound    _   _
5  jumps   jump    NOUN     NNS     Number=plur     0      ROOT    _   _
6   over   over     ADP      IN               _     5      prep    _   _
7    the    the     DET      DT               _     9       det    _   _
8   lazy   lazy     ADJ      JJ      Degree=pos     9      amod    _   _
9    dog    dog    NOUN      NN     Number=sing     6      pobj    _   SpaceAfter=No
10      .      .   PUNCT       .  PunctType=peri     5     punct   _   SpaceAfter=No
"""


@pytest.mark.parametrize(
    "filename",
    [
        "long-token-to-text",
        "empty-node",
        "multiword",
        "space-after-no",
        "paragraph-and-document",
        "en_ewt-ud-test_excerp",
        "paragraph-in-sentence",
        "sentence-comments",
    ],
)
def test_parse(
    filename: str,
    snapshot: SnapshotAssertion,
) -> None:
    source_dir = Source("assets/texts")
    filename_ = SourceFilename(filename)
    with (
        mock.patch.object(Text, "write") as text_write_mock,
        mock.patch.object(Output, "write") as _output_write_mock,
        mock.patch.object(SourceStructure, "write") as source_structure_write_mock,
    ):
        parse(filename_, source_dir)
    assert text_write_mock.call_args_list == snapshot
    # assert output_write_mock.call_args_list == snapshot
    assert source_structure_write_mock.call_args_list == snapshot


@pytest.mark.parametrize(
    "filename",
    [
        "assets/texts/long-token-to-text.conllu",
        "assets/texts/empty-node.conllu",
        "assets/texts/multiword.conllu",
        "assets/texts/space-after-no.conllu",
        "assets/texts/paragraph-and-document.conllu",
        "assets/texts/en_ewt-ud-test_excerp.conllu",
        "assets/texts/paragraph-in-sentence.conllu",
        "assets/texts/sentence-comments.conllu",
    ],
)
def test_analyze_conllu(filename: str, snapshot: SnapshotAssertion) -> None:
    actual = analyze_conllu(Path(filename))

    assert actual == snapshot


def test_find_root(snapshot: SnapshotAssertion) -> None:
    with Path("assets/texts/deprel-cases.conllu").open(encoding="utf-8") as fp:
        for sentence in conllu.parse_incr(fp):
            for token in sentence:
                id_ = token["id"]
                if isinstance(id_, tuple) and id_[1] == "-":
                    root = _find_root(id_, sentence)
                    assert root == snapshot


def test_parser_parse(snapshot: SnapshotAssertion) -> None:
    parser = SparvCoNLLUParser(Source("assets/texts"))
    parser.parse(SourceFilename("deprel-cases"))

    assert parser.data == snapshot
