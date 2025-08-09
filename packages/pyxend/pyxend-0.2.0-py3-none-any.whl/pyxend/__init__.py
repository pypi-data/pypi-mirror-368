import sys
from json import loads, dumps
from enum import Enum

class ModalType(Enum):
    r"""
    Enum for modal popup types.
    ### Values:
     - **INFO**: Show a modal with an blue informational (i) icon
     - **WARNING**: Show a modal with an yellow warning /!\ icon
     - **ERROR**: Show a modal with an red error (x) icon
    """
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'

class InsertTextPreset(Enum):
    """
    Enum for predefined positions to insert text.
    ### Values:
     - **START**: Insert text at the start of file
     - **CUSTOM**: Insert text at custom position. Requires `line` and `character` provided in argumnets
     - **CURSOR**: Insert text after cursor
     - **END**: Insert text at the end of file
    """
    START = 'start'
    CUSTOM = 'custom'
    CURSOR = 'cursor'
    END = 'end'

class ReplaceTextPreset(Enum):
    """
    Enum for predefined positions to replace text.
    """
    SELECTED = 'selected'
    CUSTOM = 'custom'
    ALL = 'all'


class Extension:
    """
    Pyxend base class for building Python-powered VS Code extensions.

    Use this to define commands and return actions (e.g. modals, file edits).
    Each command is called by JS with full editor context.

    Example usage:
        ext = Extension()

        @ext.command("hello", "Say Hello")
        def hello(ctx):
            ext.show_modal("Hello World!")

        ext.run()
    """
    def __init__(self) -> None:
        """Init your extension"""
        self.commands = {}
        self.step = 0
        self.actions = []

    def command(self, name: str, title: str | None = None):
        """Command decorator  
        ### Using:
        ```python
        from pyxend import Extension

        ext = Extension()
        @ext.command(COMMAND_NAME, COMMAND_TITLE)
        def COMMAND_NAME(context):
            #your code here
            pass
        ext.run()
        ```

        ### Args:
            **name (str):** command name
            **title (str, optional):** command title. Defaults to None.

        ### Context:
        on function execute, pyxend add context to arguments.  
        Now it contains selected_text, language, cursor_pos, file_path, all_text
        #### Example:
        ```python
        @ext.command('getContext')
        def get_context(context):
            print(context)
        ```
        -> `{'selected_text': 'hello', 'language': 'text', 'cursor_pos': {'line': 1, 'character': 4}, 'file_path': ...}`
        You can see full documentation about context in README.md (pyxend -> Extension API -> Command decorator -> Context)
        """
        def decorator(fn):
            """Decorator for command"""
            self.commands[name] = fn
            return fn
        return decorator

    def show_modal(self, message: str, type: ModalType = ModalType.INFO) -> None:
        """Show modal

        ### Args:
            **message (str):** message
            **type (ModalType):** modal type (info, warning or error)
        """
        self.actions.append({"action": "show_modal", "message": message, "type": type.value})

    def replace_selected_text(self, text: str) -> None:
        """Replace selected text (deprecated)

        ### Args:
            **text (str):** text to replace
        """
        self.actions.append({"action": "replace_selected_text", "text": text})

    def replace_all_text(self, text: str) -> None:
        """Replace all text (deprecated)

        ### Args:
            **text (str):** text to replace
        """
        self.actions.append({"action": "overwrite_file", "text": text})

    def replace_text(self, text: str, preset: ReplaceTextPreset = ReplaceTextPreset.CUSTOM,
            start_line: int = 0, start_character: int = 0, end_line: int = 0, end_character: int = 0) -> None:
        """Replace text

        ### Args:
            **text (str):** text to replace
            **preset (ReplaceTextPreset):** position preset (start / custom / cursor / end). Defaults to CUSTOM
            **start_line (int):** start line number to replace text. Requires only when preset is CUSTOM. Default to 0
            **start_character (int):** start character number to replace text. Requires only when preset is CUSTOM. Default to 0
            **end_line (int):** end line number to replace text. Requires only when preset is CUSTOM. Default to 0
            **end_character (int):** end character number to replace text. Requires only when preset is CUSTOM. Default to 0
        """
        #TODO: validation
        self.actions.append({"action": "replace_text", "text": text, "preset": preset.value,
            "start": {"line": start_line, "character": start_character}, "end": {"line": end_line, "character": end_character}})


    def insert_text(self, text: str, preset: InsertTextPreset = InsertTextPreset.CUSTOM, line: int = 0, character: int = 0) -> None:
        """Insert text

        ### Args:
            **text (str):** text to insert
            **preset (InsertTextPreset):** position preset (start / custom / cursor / end). Defaults to CUSTOM
            **line (int):** line number to insert text. Requires only when preset is CUSTOM. Default to 0
            **character (int):** character number to insert text. Requires only when preset is CUSTOM. Default to 0
        """
        self.actions.append({"action": "insert_text", "text": text, "preset": preset.value, "line": line, "character": character})

    def open_file(self, path: str) -> None:
        """Open file in editor

        ### Args:
            **path (str):** file path
        """
        self.actions.append({"action": "open_file", "path": path})

    def set_cursor_pos(self, line: int, character: int) -> None:
        """Set cursor position

        ### Args:
            **line (int):** line number
            **character (int):** character number
        """
        self.actions.append({"action": "set_cursor_pos", "line": line, 'character': character})

    def save_file(self) -> None:
        """Save file"""
        self.actions.append({"action": "save_file"})

    def run_terminal_command(self, command: str, name: str = 'pyxend terminal') -> None:
        """Run terminal command (create terminal, show it, execute command)

        ### Args:
            **command (str):** command to execute
            **name (str, optional):** terminal name. Defaults to pyxend terminal
        """
        self.actions.append({"action": "run_terminal_command", "command": command, "terminal_name": name})

    def delete_selected_text(self):
        """Delete currently selected text"""
        self.actions.append({"action": "delete_selected_text"})

    def delete_file(self):
        """Delete currently opened file. Do not recommend to use"""
        self.actions.append({"action": "delete_file"})

    #TODO: more functions from JS

    def run(self) -> None:
        """Run your extension  
        If you want to test extension, execute as `python main.py COMMAND_NAME CONTEXT`
        """
        args = sys.argv[1:]
        if not args:
            print(dumps({"error": "Missing command"}))
            return
        if len(args) < 2:
            print(dumps({"error": "Missing context"}))
            return

        command = args[0]
        if command in self.commands:
            try:
                context = loads(args[1])
            except Exception as e:
                print(dumps({"error": f"Invalid JSON context: {str(e)}"}))
                return
            self.commands[command](context)
            print(dumps(self.actions))
            self.actions.clear()
        else:
            print(dumps({"error": "Unknown command"}))
