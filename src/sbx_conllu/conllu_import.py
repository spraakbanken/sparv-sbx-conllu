"""Importer for CoNLL-U files."""

import operator
import typing as t
from collections import defaultdict
from pathlib import Path

import conllu
import sparv.api
from sparv.api import Config, Output, Source, SourceFilename, SourceStructure, SourceStructureParser, Text, importer

logger = sparv.api.get_logger(__name__)

CONLLU_EXTENSION_NAME: str = "conllu"
CONLLU_EXTENSION: str = f".{CONLLU_EXTENSION_NAME}"


class XMLStructure(SourceStructureParser):
    """Class to get and store XML structure."""

    @staticmethod
    def setup() -> dict:
        """Return setup wizard."""
        return {
            "type": "select",
            "name": "scan_conllu",
            "message": "What type of scan do you want to do?",
            "choices": [
                {
                    "name": "Scan ALL my files, since markup may differ between them "
                    "(this might take some time if the corpus is big).",
                    "value": "all",
                },
                {
                    "name": "Scan ONE of my files at random. All files contain the same markup, so scanning "
                    "one is enough.",
                    "value": "one",
                },
            ],
        }

    def get_annotations(self, corpus_config: dict) -> list[str]:  # noqa: ARG002
        """Get, store and return XML structure.

        Returns:
            List of elements and attributes in the XML file.
        """
        if self.annotations is None:
            elements: set[str] = set()
            conllu_files = self.source_dir.glob("**/*.conllu")
            if self.answers.get("scan_xml") == "all":
                for conllu_file in conllu_files:
                    elements = elements.union(analyze_conllu(conllu_file))
            else:
                elements = analyze_conllu(next(conllu_files))

            self.annotations = sorted(elements)  # type: ignore[assignment]
        return t.cast(list[str], self.annotations)


@importer(
    "Import CoNLL-U files",
    file_extension=CONLLU_EXTENSION_NAME,
    outputs=[Config("sbx_conllu.import_attributes")],
    config=[
        Config(
            "sbx_conllu.import_attributes",
            ["text"],
            description="List of attributes that is needed for other analysis.",
            datatype=list[str],
        )
    ],
    text_annotation="text",
)
def parse(
    filename: SourceFilename = SourceFilename(),
    source_dir: Source = Source(),
    # out_sentence: Output = Output("sbx_conllu.sentence", cls="sentence"),
) -> None:
    """Import text from CoNLL-U files."""
    parser = SparvCoNLLUParser(source_dir)
    parser.parse(filename)
    # raise SparvErrorMessage(f"The CoNLL-U input file could not be parsed. Error: {e!s}") from None
    parser.save()


class _Instance(t.TypedDict):
    name: str
    start: tuple[int, int]
    end: tuple[int, int]
    attrs: dict[str, t.Any]


class _Element(t.TypedDict):
    attrs: set[str]
    elements: list[_Instance]


# TEXT_SUBPOS_START should always be smallest
# and all others should have lower values than
# there included structures
TEXT_SUBPOS_START: int = 0
SENTENCE_SUBPOS_START: int = 1
TOKEN_SUBPOS_START: int = 2

# TEXT_SUBPOS_END should always be greatest
# and all others should have higher values than
# there included structures
TEXT_SUBPOS_END: int = 2
SENTENCE_SUBPOS_END: int = 1
TOKEN_SUBPOS_END: int = 0


class SparvCoNLLUParser:
    """CoNLL-U parser class for parsing CoNLL-U files."""

    def __init__(self, source_dir: Source) -> None:
        """Initialize the parser.

        Args:
            source_dir: where the files are placed.
        """
        self.source_dir = source_dir
        self.file: SourceFilename | None = None
        self.sentences: list[str] = []
        self.data: dict[str, _Element] = defaultdict(
            lambda: {"attrs": set(), "elements": []}
        )  # Metadata collected during parsing

    def parse(self, file: SourceFilename) -> None:
        """Parse CoNLL-U file."""
        logger.debug("parsing filename='%s'", file)
        self.file = file
        source_file = self.source_dir.get_path(self.file, CONLLU_EXTENSION)

        start_pos: int = 0
        end_pos: int = 0
        with source_file.open(encoding="utf-8") as fp:
            for sentence in conllu.parse_incr(fp):
                sentence_meta_text: str | None = sentence.metadata.get("text")
                sentence_attrs = {key: sentence.metadata[key] for key in sentence.metadata if key.startswith("sent_")}
                self.data["sentence"]["attrs"].update(sentence_attrs.keys())
                self.data["sentence"]["elements"].append(
                    {
                        "name": "sentence",
                        "start": (start_pos, SENTENCE_SUBPOS_START),
                        "end": (end_pos, SENTENCE_SUBPOS_END),
                        "attrs": sentence_attrs,
                    }
                )

                next_id = 0
                sentence_form_text = ""

                token_start = start_pos
                for token in sentence:
                    id_: int | tuple[int, str, int] = token["id"]
                    form: str = token["form"]
                    if isinstance(id_, tuple) and id_[1] == ".":
                        logger.warning(
                            "Skipping empty node (id='%s', form='%s') in %s. Tracking issue: %s",
                            _fmt_id(id_),
                            form,
                            source_file,
                            "https://github.com/spraakbanken/sparv-sbx-conllu/issues/14",
                        )
                        continue
                    if isinstance(id_, tuple):
                        next_id = id_[2]
                    elif id_ > next_id:
                        pass
                    else:
                        # TODO: handle skipped token, see https://github.com/spraakbanken/sparv-sbx-conllu/issues/15
                        logger.warning(
                            "Skipping token (id='%s', form='%s') inside multiword token in %s. Tracking issue: %s",
                            _fmt_id(id_),
                            form,
                            source_file,
                            "https://github.com/spraakbanken/sparv-sbx-conllu/issues/15",
                        )
                        continue
                    misc: dict[str, str] | None = token.get("misc")
                    space = "" if misc and misc.get("SpaceAfter") == "No" else " "
                    if sentence_meta_text is None:
                        sentence_form_text += f"{form}{space}"
                    token_attrs = {"id": _fmt_id(id_)}
                    if lemma := token.get("lemma"):
                        token_attrs["baseform"] = "" if lemma == "_" else lemma
                    if upos := token.get("upos"):
                        token_attrs["upos"] = "" if upos == "_" else upos
                    if xpos := token.get("xpos"):
                        token_attrs["xpos"] = xpos
                    if feats := token.get("feats"):
                        feats_str = "|".join(f"{feat}={value}" for feat, value in feats.items())
                        token_attrs["ufeats"] = f"|{feats_str}|" if feats_str else "|"
                    if head := token.get("head"):
                        token_attrs["dephead"] = head
                    if deprel := token.get("deprel"):
                        token_attrs["deprel"] = "" if deprel == "_" else deprel
                    if deps := token.get("deps"):
                        deps_str = "|".join(f"{dep}={rel}" for dep, rel in deps)
                        if deps_str:
                            token_attrs["deps"] = f"|{deps_str}|"
                    if misc := token.get("misc"):
                        misc_str = "|".join(f"{key}={value}" for key, value in misc.items())
                        if misc_str:
                            token_attrs["misc"] = f"|{misc_str}|"
                    token_end = token_start + len(form)
                    self.data["token"]["attrs"].update(token_attrs.keys())
                    self.data["token"]["elements"].append(
                        {
                            "name": "token",
                            "start": (token_start, TOKEN_SUBPOS_START),
                            "end": (token_end, TOKEN_SUBPOS_END),
                            "attrs": token_attrs,
                        }
                    )
                    logger.debug(
                        "added token id=%s start=%s, end=%s",
                        token_attrs["id"],
                        self.data["token"]["elements"][-1]["start"],
                        self.data["token"]["elements"][-1]["end"],
                    )
                    token_start = token_end + len(space)
                sentence_text = sentence_meta_text or sentence_form_text
                self.sentences.append(sentence_text)
                logger.debug("sentence_text=%s", sentence_text)
                sentence_length = len(sentence_text)
                end_pos += sentence_length
                # update end_pos for sentence
                self.data["sentence"]["elements"][-1]["end"] = (end_pos, SENTENCE_SUBPOS_END)
                logger.debug(
                    "added sentence start=%s, end=(%d, %d)",
                    self.data["sentence"]["elements"][-1]["start"],
                    end_pos,
                    SENTENCE_SUBPOS_END,
                )
                # handle whitespace between sentences
                end_pos += 1
                start_pos = end_pos

    def save(self) -> None:
        """Save text data and annotation files to disk."""
        if self.file is None:
            raise RuntimeError("file is None. This shouldn't happen")
        file: str = self.file
        logger.info("saving data parsed from filename='%s'", file)

        logger.debug("writing text from filename=%s", file)
        text = " ".join(self.sentences)
        Text(file).write(text)

        logger.debug("writing text spans from filename=%s", file)
        full_element = "text"
        spans = [((0, TEXT_SUBPOS_START), (len(text), TEXT_SUBPOS_END))]
        Output(full_element, source_file=file).write(spans)

        structure: list[str] = ["text", "sentence"]
        for element_name, element in self.data.items():
            spans = []
            attributes: dict[str, list[t.Any]] = {attr: [] for attr in element["attrs"]}
            for instance in element["elements"]:
                spans.append((instance["start"], instance["end"]))
                for attr in attributes:  # noqa: PLC0206
                    attributes[attr].append(instance["attrs"].get(attr, ""))

            full_element = f"{element_name}"
            structure.append(full_element)

            # Sort spans and annotations by span position (required by Sparv)
            if attributes and spans:
                attr_names, attr_values = list(zip(*attributes.items(), strict=True))
                spans, *attr_values = list(  # type:ignore[assignment]
                    zip(*sorted(zip(spans, *attr_values, strict=True), key=operator.itemgetter(0)), strict=True)
                )
                attributes = dict(zip(attr_names, attr_values, strict=True))  # type: ignore[arg-type]
            else:
                spans.sort()
            logger.debug("writing %s spans from filename=%s", full_element, file)
            Output(full_element, source_file=file).write(spans)

            for attr, attr_values in attributes.items():
                full_attr = f"{full_element}:{attr}"
                logger.debug("writing %s values from filename=%s", full_attr, file)
                Output(full_attr, source_file=file).write(attr_values)
                structure.append(full_attr)

        logger.debug("writing source structure from filename=%s", file)
        # Save list of all elements and attributes to a file (needed for export)
        structure.sort()
        SourceStructure(file).write(structure)


def _fmt_id(id_: int | tuple[int, str, int]) -> str:
    if isinstance(id_, int):
        return f"{id_}"
    return f"{id_[0]}{id_[1]}{id_[2]}"


def analyze_conllu(source_file: Path) -> set[str]:
    """Analyze an XML file and return a list of elements and attributes.

    Args:
        source_file: The XML file to analyze.

    Returns:
        A set of elements and attributes found in the XML file.
    """
    elements = {"text", "token"}

    with source_file.open(encoding="utf-8") as fp:
        for line in fp:
            if line.startswith("#"):
                attr = line[1:].split("=")[0].strip()
                if attr == "text":
                    elements.add(attr)
                elif attr.startswith("sent_"):
                    elements.add("sentence")
                    elements.add(f"{attr}")
                else:
                    logger.warning("Unknown attribute '%s', skipping ...", attr)

    return elements
