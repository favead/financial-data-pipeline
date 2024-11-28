from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from typing import Dict, List, Optional, Pattern, Tuple

import click


@dataclass
class RegexPattern:
    pattern: Optional[str]

    def compile(self) -> Optional[Pattern]:
        if not isinstance(self.pattern, str):
            print(
                f"Invalid pattern type: {type(self.pattern)}. Expected a string."
            )
            return None
        try:
            return re.compile(self.pattern)
        except re.error:
            return re.compile(re.escape(self.pattern))


@dataclass
class TextProcessingPatterns:
    before_first_chapter: Optional[Pattern]
    after_last_chapter: Optional[Pattern]
    chapter_separator: Optional[Pattern]
    in_chapters: List[Dict[str, Optional[Pattern]]]
    inline_patterns: List[Optional[Pattern]]

    @classmethod
    def from_config(cls, config: Dict) -> "TextProcessingPatterns":
        remove_patterns = config.get("remove_patterns", {})
        return cls(
            before_first_chapter=RegexPattern(
                remove_patterns.get("before_first_chapter")
            ).compile(),
            after_last_chapter=RegexPattern(
                remove_patterns.get("after_last_chapter")
            ).compile(),
            chapter_separator=RegexPattern(
                remove_patterns.get("chapter_separator")
            ).compile(),
            in_chapters=[
                {
                    "from": RegexPattern(chapter.get("from")).compile(),
                    "to": RegexPattern(chapter.get("to")).compile(),
                }
                for chapter in remove_patterns.get("in_chapters", [{}])
            ],
            inline_patterns=[
                RegexPattern(pattern.get("pattern")).compile()
                for pattern in remove_patterns.get("inline_patterns", [])
            ],
        )


class TextLineProcessor:
    def __init__(self, patterns: TextProcessingPatterns):
        self.patterns = patterns
        self.before_first_chapter_passed = False
        self.ignore_text = False
        self.current_chapter = None

    def should_process_line(self, line: str) -> bool:
        if self._check_before_first_chapter(line):
            self.before_first_chapter_passed = True
            return True

        if self._check_after_last_chapter(line):
            return False

        if not self.before_first_chapter_passed:
            return False

        if self.current_chapter:
            self.ignore_text = self._check_in_chapters_to(line)
            if not self.ignore_text:
                self.current_chapter = None
            return False

        self.ignore_text, self.current_chapter = self._check_in_chapters_from(
            line
        )
        if self.ignore_text:
            return False

        return not self._check_inline_patterns(line) and len(line.strip()) > 0

    def _check_before_first_chapter(self, line: str) -> bool:
        return bool(
            self.patterns.before_first_chapter
            and self.patterns.before_first_chapter.match(line)
        )

    def _check_after_last_chapter(self, line: str) -> bool:
        return bool(
            self.patterns.after_last_chapter
            and self.patterns.after_last_chapter.match(line)
        )

    def _check_inline_patterns(self, line: str) -> bool:
        return any(
            pattern and pattern.match(line)
            for pattern in self.patterns.inline_patterns
        )

    def _check_in_chapters_from(
        self, line: str
    ) -> Tuple[bool, Optional[Dict[str, Pattern]]]:
        for pattern in self.patterns.in_chapters:
            if pattern["from"] and pattern["from"].match(line):
                return True, pattern
        return False, None

    def _check_in_chapters_to(self, line: str) -> bool:
        return not bool(
            self.current_chapter
            and self.current_chapter["to"]
            and self.current_chapter["to"].match(line)
        )


class TextFileProcessor:
    def __init__(self, patterns: TextProcessingPatterns):
        self.line_processor = TextLineProcessor(patterns)

    def process_file(self, input_path: Path, output_path: Path) -> None:
        print(f"Processing text data from {input_path}")

        processed_text = []
        total_length = 0

        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                total_length += len(line)
                if self.line_processor.should_process_line(line):
                    processed_text.append(line)

        result = "".join(processed_text)
        result_len = len(result)

        print(
            f"Original file length: {total_length}, "
            f"processed file length: {result_len}"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)


# CLI interface remains the same
@click.command()
@click.option(
    "--pdf_dir",
    type=click.Path(exists=True),
    help="Path to the pdf directory",
)
@click.option(
    "--txt_dir",
    type=click.Path(exists=True),
    help="Path to the txt directory",
)
def main(pdf_dir: str, txt_dir: str) -> None:
    """
    Preprocess text data from raw txt files with cleaning configuration,
    which is specified in the meta.json file in each textbook directory.
    After processing, save the processed text to the processed directory.

    Parameters:
    ----------
    pdf_dir: str
        Path to the pdf directory.
    txt_dir: str
        Path to the txt directory.

    Returns:
    -------
    None
    """
    txt_dir_path: Path = Path(txt_dir)
    pdf_dir_path: Path = Path(pdf_dir)
    processed_txt_dir = txt_dir_path / "processed"
    raw_txt_dir = txt_dir_path / "raw"
    os.makedirs(processed_txt_dir, exist_ok=True)

    for raw_txt_file_path in raw_txt_dir.glob("*.txt"):
        pdf_textbook_dirname = raw_txt_file_path.stem
        meta_path = pdf_dir_path / pdf_textbook_dirname / "meta.json"

        if not meta_path.exists():
            continue

        with open(meta_path, "r") as f:
            processing_config = json.load(f)

        patterns = TextProcessingPatterns.from_config(processing_config)
        processor = TextFileProcessor(patterns)
        processor.process_file(
            raw_txt_file_path, processed_txt_dir / raw_txt_file_path.name
        )


if __name__ == "__main__":
    main()
