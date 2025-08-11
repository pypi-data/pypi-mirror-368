import re
from pathlib import Path

from robotooter.bots.serializer.models import BookMetadata, ChapterMetadata
from robotooter.file_filter import FileFilter
from robotooter.filters.base_filter import BaseFilter
from robotooter.filters.gutenberg import GutenbergFilter
from robotooter.filters.paragraph_combining import ParagraphCombiningFilter

RE_PART = re.compile(r"^PART (.+?)\.$")
RE_CHAPTER = re.compile(r"^CHAPTER (.+?)\.$")

class Processor:
    def __init__(self, working_directory: Path):
        self.filters: list[BaseFilter] = [GutenbergFilter(), ParagraphCombiningFilter()]
        self.working_directory = working_directory
        self.output_dir = working_directory / "output"

    def process_file(self) -> None:
        file_path = self.output_dir / 'processed.txt'
        with open(file_path, "r") as file:
            title = file.readline().strip()
            file.readline()
            author = file.readline().strip()

            # skip next few lines
            for _ in range(5):
                file.readline()

            # skip through contents
            line = ''
            while line.strip() != f"{title}.":
                line = file.readline()

            # We're now down with the front matter
            counter = 0
            section = ''
            section_title = ''
            section_start = False
            chapter = ''
            chapter_title = ''
            chapter_lines: list[str] = []
            for raw_line in file:
                line = raw_line.strip()

                if RE_PART.match(line):
                    section = line
                    section_title = ''
                    continue

                if RE_CHAPTER.match(line):
                    chapter = line
                    chapter_title = ''
                    continue

                if section and not section_title:
                    section_title = line
                    section_start = True
                    continue

                if chapter and not chapter_title:
                    chapter_title = line

                    if chapter_lines:
                        self.chunk_chapter(counter, chapter_lines)
                        chapter_lines = []
                    counter += 1

                    chapter_metadata = ChapterMetadata(
                        section=section,
                        section_title=section_title,
                        section_start=section_start,
                        chapter=chapter,
                        chapter_title=chapter_title,
                        chapter_start=True
                    )
                    with open(self._chapter_metadata_path(counter), "w") as md_file:
                        md_file.write(chapter_metadata.model_dump_json(indent=2))
                    section_start = False

                    chapter_lines.append(f"{chapter}\n{chapter_title}\n")
                    continue

                if chapter_title:
                    chapter_lines.append(raw_line)
            if chapter_lines:
                self.chunk_chapter(counter, chapter_lines)

            book_metadata = BookMetadata(
                title=title,
                author=author,
                total_days=counter
            )
            with open(self.output_dir / "book_metadata.json", "w") as md_file:
                md_file.write(book_metadata.model_dump_json(indent=2))

    def chunk_chapter(self, chapter: int, text: list[str]) -> None:
        max_length = 2000
        chunk = ''
        part = 1
        for line in text:
            if len(chunk) + len(line) >= max_length:
                self._write_chunk(chapter, part, chunk)
                part += 1
                chunk = ''
            chunk += line
        if chunk:
            self._write_chunk(chapter, part, chunk)

    def _write_chunk(self, chapter: int, part: int, chunk: str) -> None:
        c = str(chapter).zfill(4)
        p = str(part).zfill(4)
        chunk_path = self.output_dir / f"{c}_{p}.txt"
        with open(chunk_path, "w") as chunk_file:
            chunk_file.write(chunk)

    def _chapter_metadata_path(self, chapter: int) -> Path:
        base = f"{str(chapter).zfill(4)}"
        return self.output_dir / f"{base}_metadata.json"


    def preprocess_file(self, file_path: str) -> None:
        full_path = self.working_directory / file_path
        output_dir = self.working_directory / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "processed.txt"

        file_filter = FileFilter(self.filters)
        file_filter.process_file(full_path, output_path)


