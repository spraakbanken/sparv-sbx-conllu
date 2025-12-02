"""Tool for printing a dep-tree."""

import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def main() -> None:
    """Print dep-tree for given file."""
    corpus_path = Path(sys.argv[1])

    if corpus_path.suffix == ".xml":
        print_tree_from_xml(corpus_path)
    else:
        print(f"Unsupported file type: '{corpus_path.suffix}'", file=sys.stderr)
        sys.exit(1)


def print_tree_from_xml(corpus_path: Path) -> None:
    """Print dep-tree from a XML file."""
    tree = ET.parse(corpus_path)
    root = tree.getroot()
    for sentence in root.iter("sentence"):
        if sent_id := sentence.attrib.get("sent_id"):
            print(f"{{'sent_id': '{sent_id}'}}")
        tree_ = _to_tree(sentence)
        _print_tree_from_sentence_xml(tree_)
        print()


def _print_tree_from_sentence_xml(token: ET.Element, depth: int = 0) -> None:
    node_repr = " ".join([f"form:{token.text}", f"lemma:{token.attrib['baseform']}", f"upos:{token.attrib['pos_ud']}"])
    print(
        "{indent}(deprel:{deprel}) {node_repr} [{idx}]".format(
            indent=" " * depth * 4, deprel=token.attrib["deprel_ud"], node_repr=node_repr, idx=token.attrib["id"]
        )
    )
    for child in token:
        _print_tree_from_sentence_xml(child, depth + 1)


def _head_to_token(sentence: ET.Element) -> dict[int, list[ET.Element]]:
    head_indexed = defaultdict(list)
    for token in sentence.iter("token"):
        # print(f"attrib={token.attrib}")
        if "dephead_ud" not in token.attrib:
            continue
        head = int(token.attrib["dephead_ud"])
        if head < 0:
            continue
        head_indexed[head].append(token)
    # print(f"{head_indexed=}")
    return head_indexed


def _create_elem(tag: str, attrib: dict, text: str | None, children: list[ET.Element] | None = None) -> ET.Element:
    elem = ET.Element(tag, attrib=attrib)
    elem.text = text or ""
    elem.extend(children or [])
    return elem


def _to_tree(sentence: ET.Element) -> ET.Element:
    def _create_tree(head_to_token_mapping: dict[int, list[ET.Element]], id_: int = 0) -> list[ET.Element]:
        return [
            _create_elem(
                child.tag, child.attrib, child.text, _create_tree(head_to_token_mapping, int(child.attrib["id"]))
            )
            for child in head_to_token_mapping[id_]
        ]

    head_indexed = _head_to_token(sentence)
    if len(head_indexed[0]) > 1:
        head_indexed[-1] = [_create_elem("token", {"id": 0, "deprel_ud": "root"}, "_")]
        root = _create_tree(head_indexed, -1)[0]
    else:
        root = _create_tree(head_indexed, 0)[0]
    return root


if __name__ == "__main__":
    main()
