import logging
from textual.app import App, ComposeResult, RenderResult
from textual.containers import Vertical
from textual.events import CursorPosition
from textual.logging import TextualHandler
from textual.widget import Widget
from textual.widgets import Static
from wcwidth import wcwidth

class FileText():
    def __init__(self, path: str):
        self.path = path
        if self.path:
            with open(path) as file:
                self.content = [line.rstrip('\n') for line in file]
        else:
            self.content = []

class EditArea(Widget):

    def __init__(self, text: list[str]):
        super().__init__()
        self.text = text
        self.tab_width = 4

    def render(self) -> RenderResult:
        display_list = []
        text_len = len(self.text)
        text_y = 0
        text_x = 0
        line: str | None = None
        line_len = 0

        width = self.content_size.width
        height = self.content_size.height
        for y in range(height):
            if text_y >= text_len:
                break
            if line is None:
                line = self.text[text_y]
                line_len = len(line)
                text_x = 0
                if line == '':
                    display_list.append(line)
                    line = None
                    text_y += 1
                    continue
            index, piece = self.visualize_text(line[text_x:], width)
            text_x += index
            display_list.append(piece)
            if text_x == line_len:
                line = None
                text_y += 1

        return '\n'.join(display_list)

    def visualize_text(self, string: str, width: int):
        index = 0
        accumulate = 0
        result_list = []

        for char in string:
            if char == '\t':
                char_width = self.tab_width
                char_to_append = ' ' * self.tab_width
            elif char == '[':
                char_width = 1
                char_to_append = '\\['
            else:
                char_width = wcwidth(char)
                char_to_append = char

            if char_width > 0:
                next_accumulate = accumulate + char_width
                if next_accumulate > width:
                    break
                else:
                    accumulate = next_accumulate
                    result_list.append(char_to_append)
            index += 1
        result = ''.join(result_list)
        self.log(f'width: {width}: "{result}"')

        return index, ''.join(result_list)


class EditPanel(Widget):
    def __init__(self, file_text: FileText):
        super().__init__()
        self.file_text = file_text

    def compose(self) -> ComposeResult:
        self.edit_area = EditArea(self.file_text.content)
        self.edit_area.styles.width = '100%'
        self.edit_area.styles.height = '1fr'

        self.bar = Static(self.file_text.path)
        self.bar.styles.width = '100%'
        self.bar.styles.height = 1
        with Vertical():
            yield self.edit_area
            yield self.bar

class EditorWidget(Widget):

    def __init__(self, path_list: list[str]):
        super().__init__()
        self.file_dict = {
            index: FileText(path) for index, path in enumerate(path_list)
        }

    def compose(self) -> ComposeResult:
        if self.file_dict:
            keys = self.file_dict.keys()
            key = next(iter(keys))
            file_text = self.file_dict[key]
            self.panel = EditPanel(file_text)
        else:
            self.file_dict[0] = FileText('')
            self.panel = EditPanel(self.file_dict[0])
        self.panel.styles.width = '100%'
        self.panel.styles.height = '1fr'

        self.bar = Static('NOR: Press Ctrl+Q to Exit')
        self.bar.styles.width = '100%'
        self.bar.styles.height = 1
        with Vertical():
            yield self.panel
            yield self.bar

class Editor(App):
    TITLE = 'Pelyx'
    SUB_TITLE = 'a terminal text editor'

    def __init__(self, path_list: list[str]):
        super().__init__()
        self.editor = EditorWidget(path_list)

    def compose(self) -> ComposeResult:
        self.editor.styles.width = '100%'
        self.editor.styles.height = '100%'
        yield self.editor
