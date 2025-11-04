from unittest import mock

from sparv.api import Output, Source, SourceFilename, SourceStructure, Text
from syrupy.assertion import SnapshotAssertion

from sbx_conllu.conllu_import import SparvCoNLLUParser

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


@mock.patch.object(SourceStructure, "write")
@mock.patch.object(Output, "write")
@mock.patch.object(Text, "write")
def test_conllu_parser(
    text_write_mock: mock.MagicMock,
    output_write_mock: mock.MagicMock,
    source_structure_write_mock: mock.MagicMock,
    snapshot: SnapshotAssertion,
) -> None:
    parser = SparvCoNLLUParser(Source("assets/texts"))
    parser.parse(SourceFilename("long-token-to-text"))
    parser.save()
    assert text_write_mock.call_args == snapshot
    assert output_write_mock.call_args == snapshot
    assert source_structure_write_mock.call_args == snapshot
