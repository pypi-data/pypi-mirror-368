import os
from typing import List, Dict

from bluer_objects import file

from bluer_journal.classes.journal import journal
from bluer_journal.logger import logger


class JournalPage:
    def __init__(
        self,
        title: str,
        load: bool = True,
        verbose: bool = False,
    ):
        assert title

        self.title = title
        self.verbose = verbose

        self.content: List[str] = []
        self.sections: Dict[str, List[str]] = {}

        if load:
            assert self.load(), f"cannot load {self.title}"

    @property
    def filename(self) -> str:
        return os.path.join(
            journal.path,
            f"{self.title}.md",
        )

    def generate(self):
        self.content = []
        for section_name, lines in sorted(self.sections.items()):
            if section_name:
                self.content.append(f"# {section_name}")

            self.content += lines + [""]

        self.remove_double_blanks()

    def list_of_todos(
        self,
        log: bool = True,
    ) -> List[str]:
        todos: List[str] = []
        for section_content in self.sections.values():
            todos_all = [
                line.split("- [ ]", 1)[1].strip()
                for line in section_content
                if line.startswith("- [ ]")
            ]

            for todo_item in todos_all:
                todos += [todo_item]
                if "waiting" in todo_item:
                    break

        if log and todos:
            logger.info(f"{self.title}: {len(todos)} todo(s)")
            for index, todo_item in enumerate(todos):
                logger.info(f"#{index+1: 2d}. {todo_item}")

        return todos

    def load(
        self,
        parse: bool = True,
    ) -> bool:
        success, self.content = file.load_text(
            self.filename,
            ignore_error=True,
            log=self.verbose,
        )
        if not success:
            return success

        if not parse:
            return True

        self.sections = {"": []}

        current_section = ""
        for line in self.content:
            if line.startswith("#"):
                current_section = line.split("#", 1)[1].strip()
                self.sections[current_section] = []
                continue

            self.sections[current_section].append(line)

        if not self.sections[""]:
            del self.sections[""]

        if self.verbose:
            logger.info(
                "{}: {} section(s) from {}: {}".format(
                    self.title,
                    len(
                        self.sections,
                    ),
                    self.title,
                    ", ".join(self.sections.keys()),
                )
            )

        return True

    def remove_double_blanks(self):
        content_ = [line for line in self.content]
        self.content = []

        prev_blank = False
        for line in content_:
            if line.strip() == "":
                if not prev_blank:
                    self.content.append(line)
                prev_blank = True
            else:
                self.content.append(line)
                prev_blank = False

    def save(
        self,
        log: bool = True,
        generate: bool = True,
    ) -> bool:
        if generate:
            self.generate()

        return file.save_text(
            self.filename,
            self.content,
            log=log,
        )
