"""Importer for CoNLL-U files."""

import conllu
import sparv.api
from sparv.api import Output, Source, SourceFilename, SourceStructure, Text, importer

logger = sparv.api.get_logger(__name__)

CONLLU_EXTENSION_NAME: str = "conllu"
CONLLU_EXTENSION: str = f".{CONLLU_EXTENSION_NAME}"


@importer(
    "Import CoNLL-U files",
    file_extension=CONLLU_EXTENSION_NAME,
    outputs=["text"],
    text_annotation="text",
)
def parse(
    filename: SourceFilename = SourceFilename(),
    source_dir: Source = Source(),
) -> None:
    """Import text from CoNLL-U files."""
    parser = SparvCoNLLUParser(source_dir)
    parser.parse(filename)
    # raise SparvErrorMessage(f"The CoNLL-U input file could not be parsed. Error: {e!s}") from None
    parser.save()


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

    def parse(self, file: SourceFilename) -> None:
        """Parse CoNLL-U file."""
        logger.debug("parsing filename='%s'", file)
        self.file = file
        source_file = self.source_dir.get_path(self.file, CONLLU_EXTENSION)

        with source_file.open(encoding="utf-8") as fp:
            for sentence in conllu.parse_incr(fp):
                self.sentences.append(sentence.metadata["text"])

    def save(self) -> None:
        """Save text data and annotation files to disk."""
        if self.file is None:
            raise RuntimeError("file is None. This shouldn't happen")
        file: str = self.file
        logger.info("saving data parsed from filename='%s'", file)

        logger.debug("writing text from filename=%s", file)
        text = "".join(self.sentences)
        Text(file).write(text)

        logger.debug("writing output from filename=%s", file)
        full_element = "text"
        spans = [((0, 0), (len(text), 0))]
        Output(full_element, source_file=file).write(spans)

        logger.debug("writing source structure from filename=%s", file)
        structure: list[str] = ["text"]
        SourceStructure(file).write(structure)
