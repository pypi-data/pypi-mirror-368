import re
from io import StringIO
from pathlib import Path
from typing import Optional, List
from pptx.dml.color import RGBColor
from urllib.parse import urlparse


class OutPutter(object):

    def __init__(self):
        self.ofile = StringIO()
        self.page_image: dict[str, dict] = {}

    def put_header(self):
        pass

    def put_title(self, text, level):
        pass

    def put_list(self, text, level):
        pass

    def put_para(self, text):
        pass

    def put_image(self, path, max_width, width: Optional[int] = None, height: Optional[int] = None, suffix: Optional[str] = None):
        pass

    def put_table(self, table):
        pass

    def get_accent(self, text):
        pass

    def get_strong(self, text):
        pass

    def get_colored(self, text, rgb):
        pass

    def get_hyperlink(self, text, url):
        pass

    def get_escaped(self, text):
        pass

    def write(self, text):
        self.ofile.write(text)

    def flush(self):
        self.ofile.flush()

    def close(self):
        self.ofile.close()

    def read(self) -> str:
        return self.ofile.getvalue()

    def read_image(self) -> List[dict]:
        return list(self.page_image.values())


class MarkDownOutPutter(OutPutter):

    def __init__(self):
        super().__init__()
        self.esc_re1 = re.compile(r"([\\\*`!_\{\}\[\]\(\)#\+-\.])")
        self.esc_re2 = re.compile(r"(<[^>]+>)")

    def put_title(self, text: str, level: int) -> None:
        text_strip: str = text.strip()
        self.ofile.write(f"{'#' * level} {text_strip}\n\n")

    def put_list(self, text: str, level: int) -> None:
        self.ofile.write("  " * level + "* " + text.strip() + "\n")

    def put_para(self, text: str) -> None:
        self.ofile.write(text + "\n\n")

    def put_image(self, path: str, max_width: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, suffix: Optional[str] = None) -> None:
        if max_width is None:
            self.ofile.write(f"![]({path})\n\n")
        else:
            self.ofile.write(
                f'<img src="{path}" style="max-width:{max_width}px;" />\n\n'
            )
        if path.startswith("http"):
            self.page_image[path] = dict(
                filename=Path(urlparse(path).path).name,
                width=width,
                url=path,
                height=height,
                suffix="png"
            )

    def put_table(self, table: List[List[str]]) -> None:
        gen_table_row = (
            lambda row: "| "
            + " | ".join([c.replace("\n", "<br />") for c in row])
            + " |"
        )
        self.ofile.write(gen_table_row(table[0]) + "\n")
        self.ofile.write(gen_table_row([":-:" for _ in table[0]]) + "\n")
        self.ofile.write("\n".join([gen_table_row(row) for row in table[1:]]) + "\n\n")

    def get_accent(self, text: str) -> str:
        return f" _{text}_ "

    def get_strong(self, text: str) -> str:
        return f" __{text}__ "

    def get_colored(self, text: str, rgb: RGBColor) -> str:
        return f' <span style="color:#{str(rgb)}">{text}</span> '

    def get_hyperlink(self, text: str, url: str) -> str:
        return f"[{text}]({url})"

    def esc_repl(self, match):
        return "\\" + match.group(0)

    def get_escaped(self, text: str) -> str:
        text1: str = re.sub(self.esc_re1, self.esc_repl, text)
        text2: str = re.sub(self.esc_re2, self.esc_repl, text1)
        return text2
