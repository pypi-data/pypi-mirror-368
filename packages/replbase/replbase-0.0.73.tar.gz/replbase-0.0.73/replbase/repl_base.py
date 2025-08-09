"""

#######################################################################

    Module Name: repl_base
    Description: Base class for REPL tools
    Author: Joseph Bochinski
    Date: 2024-12-16


#######################################################################
"""

# region Imports
from __future__ import annotations

import argparse
import grp
import inspect
import math
import os
import pwd
import re
import shlex
import stat
import time

from dataclasses import dataclass, field
from enum import Enum, EnumType
from typing import Any, Callable, Literal, get_type_hints

from prompt_toolkit import PromptSession
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from ptpython.repl import embed
from rich import pretty
from rich.console import Console
from rich.theme import Theme
from tabulate import tabulate

from replbase.cmd_meta import ReplCommand, CommandMeta

# endregion Imports


# region Constants

ColorSystem = Literal["auto", "standard", "256", "truecolor", "windows"]


# endregion Constants


# region Classes


def is_num_str(val: str) -> bool:
    return bool(re.match(r"^-?\d+(\.\d+)?$", val))


def ls_liah(path: str = "."):
    """Print output similar to using `ls -liah` in the terminal"""

    files = os.listdir(path)
    files_info = []

    for file_name in files:
        # Get the full path
        full_path = os.path.join(path, file_name)

        # Get file stats
        file_stat = os.lstat(full_path)

        # Get permissions
        permissions = stat.filemode(file_stat.st_mode)

        # Get number of hard links
        hard_links = file_stat.st_nlink

        # Get UID and GID, convert to names
        uid_name = pwd.getpwuid(file_stat.st_uid).pw_name
        gid_name = grp.getgrgid(file_stat.st_gid).gr_name

        # Get file size
        size = file_stat.st_size

        # Convert size to human-readable form
        size_human = convert_size(size)

        # Get last modification time
        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(file_stat.st_mtime))

        # Append the information
        files_info.append(
            [
                file_stat.st_ino,
                permissions,
                hard_links,
                uid_name,
                gid_name,
                size_human,
                mtime,
                file_name,
            ]
        )

    # Print in tabular format
    headers = [
        "Inode",
        "Permissions",
        "Links",
        "UID",
        "GID",
        "Size",
        "Last Modified",
        "Name",
    ]
    print(tabulate(files_info, headers=headers, tablefmt="plain"))


def convert_size(size_bytes):
    """Convert a size in bytes to a human-readable string."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "K", "M", "G", "T", "P", "E", "Z", "Y")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s}{size_name[i]}"


def setvar(name: str, var: Any) -> None:
    globals()[name] = var


def setfunc(func: Callable) -> None:
    globals()[func.__name__] = func


@dataclass
class ReplTheme(Theme):
    title: str = "bold cyan"
    prompt: str = "bold green"
    warn: str = "bold yellow"
    error: str = "bold red"
    cmd_name: str = "bold green"
    cmd_desc: str = "cyan"
    exit_kw: str = "bold green"
    exit_str: str = "cyan"
    greeting: str = "cyan"
    addl_styles: dict | None = None

    def __post_init__(self) -> None:
        styles = dict(vars(self))
        extras = styles.pop("addl_styles", {})
        if extras:
            styles.update(extras)
        super().__init__(styles)


@dataclass
class ReplBase:
    """Dataclass for CLI options"""

    debug_enabled: bool | None = None
    """Debug mode enabled"""

    title: str | None = None
    """Title of the CLI REPL Prompt"""

    exit_keywords: list[str] | None = None
    """List of strings that cause the REPL to close, defaults to x, q, 
        exit, and quit"""

    init_prompt: str | list[str] | None = None
    """Prompt to display at startup"""

    color_system: ColorSystem | None = None
    """Color syste for the rich console"""

    theme: ReplTheme | dict | None = None

    console: Console | None = None
    """ Rich Console instance """

    history: str | None = None
    """Path to the prompt history file"""

    temp_file: str | None = None
    """Path to prompt temporary file"""

    style: dict | Style | None = None
    """Style for the prompt"""

    ignore_case: bool | None = None
    """Ignore case setting for the WordCompleter instance"""

    commands: dict[str, ReplCommand] | None = None
    """Command dictionary for prompt_toolkit. Keys are command names,
        values are the corresponding description/help text"""

    docstring_format: str = "google"

    parent: ReplBase | dict | None = None

    session: PromptSession | None = None

    cmd_defs: dict[str, CommandMeta] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.commands, dict):
            for cmd_name, cmd in self.commands.items():
                if isinstance(cmd, dict):
                    self.commands[cmd_name] = ReplCommand(**cmd)

        if self.debug_enabled is None:
            self.debug_enabled = False

        self.title = self.title or "CLI Tool"

        self.exit_keywords = self.exit_keywords or ["x", "q", "exit", "quit"]

        exit_kw_str = ", ".join(
            f'[exit_kw]"{kw}"[/exit_kw]' for kw in self.exit_keywords
        )
        exit_kw_pref = "Type one of " if len(self.exit_keywords) > 1 else "Type "
        exit_str = f"[exit_str]{exit_kw_pref}{exit_kw_str} to exit[/exit_str]"

        self.init_prompt = self.init_prompt or [
            f"[title]<<| {self.title} |>>[/title]",
            exit_str,
            '[greeting]Type [cmd_name]"help"[/cmd_name] to view available commands.[/greeting]',
        ]

        self.color_system = self.color_system or "truecolor"

        if isinstance(self.theme, dict):
            props = list(dict(vars(ReplTheme())).keys())
            init = {"addl_styles": {}}
            for key, value in self.theme.items():
                if key in props:
                    init[key] = value
                else:
                    init["addl_styles"][key] = value

            self.theme = ReplTheme(**init)
        elif self.theme is None:
            self.theme = ReplTheme()

        self.console = Console(color_system=self.color_system, theme=self.theme)

        if not self.history:
            history_name = re.sub(r"\s+", "_", self.title.lower())
            self.history = os.path.expanduser(f"~/.config/.{history_name}_history")

        if self.history:
            hist_dir = os.path.dirname(self.history)
            if not os.path.exists(hist_dir):
                os.makedirs(hist_dir, exist_ok=True)

        self.temp_file = self.temp_file or os.path.expanduser(
            "~/.config/.prompt_tmp"
        )

        if self.temp_file:
            temp_dir = os.path.dirname(self.temp_file)
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)

        self.style = self.style or {
            "prompt": "bold green",
            "": "default",
        }
        if isinstance(self.style, dict):
            self.style = Style.from_dict(self.style)

        self.apply_def_cmds()

    def apply_def_cmds(self) -> None:
        """Add the descriptions for the help and exit commands"""
        base_cmds: dict[str, ReplCommand] = {
            "\\[help, h]": ReplCommand(help_txt="Display this help message again"),
        }
        if self.exit_keywords:
            exit_str = ", ".join(self.exit_keywords)
            base_cmds.update(
                {
                    f"\\[{exit_str}]": ReplCommand(help_txt="Exit tool"),
                }
            )

        self.commands = self.commands or {}
        base_cmds.update(self.commands)
        self.commands = base_cmds

    def get_cmd_names(self) -> list[str]:
        """Retrieve names of commands, parsing out the help/exit commands"""

        help_str = "[help, h]"
        exit_str = f'[{", ".join(self.exit_keywords)}]'
        names: list[str] = [
            name
            for name in self.commands.keys()
            if name not in [help_str, exit_str]
        ]
        names.extend(["help", "h"])
        names.extend(self.exit_keywords)
        return names

    def print(self, *args) -> None:
        """Shortcut to console.print"""
        self.console.print(*args)

    def input(self, *args, suggestions: AutoSuggest = None) -> str:
        """Shortcut to console.input"""
        if self.session:
            return self.session.prompt(*args, auto_suggest=suggestions)
        return self.console.input(*args)

    def input_int(self, *args) -> int:
        """Parse input as int"""

        user_input = self.input(*args).strip().split(".")[0].strip()
        if is_num_str(user_input):
            return int(user_input)

    def input_bool(self, *args, true_list: list[str] = None) -> int:
        """Parse input as bool"""
        true_list = true_list or ["y", "yes"]
        true_list = [val.lower() for val in true_list]

        user_input = self.input(*args)
        return user_input.strip().lower() in true_list

    def input_prefer_int(self, *args) -> int | str:
        """Parse input as int if possible, otherwise return the string"""
        if not args:
            return 0
        user_input = self.input(*args).strip().split(".")[0].strip()
        if is_num_str(user_input):
            return int(user_input)
        return user_input

    def input_choice(self, *args, choices: list[str]) -> str:
        """Prompt for a choice from a list of options"""
        for idx, choice in enumerate(choices):
            self.print(f"[{idx+1}]: {choice}")
        choice = self.input_int(*args)
        if choice and choice > 0 and choice <= len(choices):
            return choices[choice - 1]

    def input_choice_dict(self, prompt: str, choices: dict) -> Any:
        """Similar to input_choice, but with more control over the options

        Args:
            prompt (str): String to print to the user
            choices (dict): Dict of choices; keys will be the displayed options, values will be the associated return value

        Returns:
            Any: Selected value
        """

        keys = list(choices.keys())
        for idx, choice in enumerate(keys):
            self.print(f"[{idx+1}]: {choice}")

        choice = self.input_int(prompt)
        if choice and choice > 0 and choice <= len(keys):
            key = keys[choice - 1]
            return choices[key]

    def input_obj_update(self, obj: dict[str, Any]) -> Any:

        prop_name = self.input_choice(
            "Select property to update: ", choices=list(obj.keys())
        )
        prop = obj[prop_name]

        if not prop:
            self.warn(f"{prop_name} is an invalid selection")
            return prop_name, None

        prompt = f"Enter value for {prop_name}: "
        value = prop
        if prop is str | list[str]:
            value = self.input(prompt)
        elif prop is int | list[int]:
            value = self.input_int(prompt)
        elif prop is bool:
            value = self.input_bool(prompt)
        elif isinstance(prop, EnumType):
            value = self.get_enum_val(prompt, prop)
        elif isinstance(prop, Enum):
            value = self.get_enum_val(prompt, type(prop))
        else:
            self.warn("Invalid property type")
            return prop_name, prop
        return prop_name, value

    def get_enum_val(self, prompt: str, enum_cls: EnumType) -> Enum:
        """Prompt the user to select an enum value

        Args:
            prompt (str): Prompt to display
            enum_cls (EnumType): Enum class to select from

        Returns:
            Enum: Selected enum value
        """

        options = dict(enum_cls.__members__)

        if len(options) == 1:
            return list(options.values())[0]
        else:
            return self.input_choice_dict(prompt, options)

    def debug(self, *args) -> None:
        """Print only if debug_enabled == True"""
        if self.debug_enabled:
            self.print(*args)

    def add_command(
        self,
        cmd_name: str,
        cmd_func: Callable = None,
        help_txt: str = "",
        use_parser: bool = False,
        description: str = "",
        # auto_suggest: AutoSuggest,
        **def_kwargs,
    ) -> ReplCommand:
        """Add a command to the REPL

        Args:
            cmd_name (str): Name of the command
            cmd_func (Callable, optional): Function to execute when called.
                Defaults to None.
            help_txt (str, optional): Help text to display from REPL help command.
                Defaults to "".
            use_parser (bool, optional): If true, adds an argparse.ArgumentParser
                to the new ReplCommand instance. Defaults to False.
            description (str, optional): Optional description for the
                ArgumentParser help text. Defaults to help_txt.
            def_args: Default arguments for the command function
            def_kwargs: Default keyword arguments for the command function

        Returns:
            ReplCommand: The new ReplCommand instance
        """

        new_cmd = ReplCommand(command=cmd_func, help_txt=help_txt)
        if use_parser:
            new_cmd.parser = argparse.ArgumentParser(
                description=description or help_txt,
            )
        if def_kwargs:
            new_cmd.def_kwargs = def_kwargs

        self.commands[cmd_name] = new_cmd
        return new_cmd

    def gen_command(self, cmd_name: str, hyphenate: bool = True) -> ReplCommand:
        if not hasattr(self, cmd_name):
            return

        cmd: Callable = getattr(self, cmd_name)

        if not callable(cmd):
            return

        cmd_meta = CommandMeta(func=cmd, register_cmd=self.add_command)
        self.cmd_defs[cmd_name] = cmd_meta
        return cmd_meta.gen_command(hyphenate=hyphenate)

    def setup_cmds(self, *cmd_names: list[str]) -> None:
        """Automatically configure commands based on the provided names
            The ReplCommand objects are populated based on function meta
            data retrieved from the provided function names
        Args:
            cmd_names (list[str]): List of class methods to convert to REPL commands
        """

        funcs: list[Callable] = [
            getattr(self, name)
            for name in cmd_names
            if hasattr(self, name) and callable(getattr(self, name))
        ]

        for func in funcs:
            help_text = func.__doc__
            name = func.__name__
            self.add_command(name, func, help_txt=help_text)

    def setup_cmds_2(self, *cmd_names: str, hyphenate: bool = True):
        for name in cmd_names:
            self.gen_command(name, hyphenate=hyphenate)

    def get_local_funcs(self, tgt_cls: type = None) -> list[str]:
        """Retrieve a list of local functions for this class

        Returns:
            list[str]: List of function names
        """

        base_funcs = [
            name
            for name in dir(ReplBase)
            if callable(getattr(ReplBase, name)) and not name.startswith("_")
        ]

        tgt_cls = tgt_cls or self.__class__

        return [
            name
            for name in dir(tgt_cls)
            if callable(getattr(tgt_cls, name))
            and not name.startswith("_")
            and name not in base_funcs
        ]

    def warn(self, msg: str) -> None:
        """Print a message to the REPL preformatted as a warning"""

        self.print(f"[warn]{msg}[/warn]")

    def pretty_print(self, obj: Any) -> None:
        pretty.pprint(obj)

    def pwd(self) -> str:
        """Print out the current path location

        Returns:
            str: The current path
        """

        self.print(f"Current location: {os.getcwd()}")
        return os.getcwd()

    def cd(self, path: str = "..") -> str:
        """Move the terminal to a new path location

        Args:
            path (str, optional): Path to move to. Defaults to "..".

        Returns:
            str: The new location
        """

        try:
            os.chdir(path)
        except FileNotFoundError:
            self.warn(
                f"Path: {path} does not exist, remaining in current directory"
            )
        new_pwd = os.getcwd()
        self.print(f"New dir: {new_pwd}")
        return new_pwd

    def ls(self, path: str = ".") -> list[str]:
        """List metadata about the files/directories at the given path

        Args:
            path (str, optional): Path to list. Defaults to ".".

        Returns:
            list[str]: List of file and directory names at the location
        """

        ls_liah(path)
        return os.listdir(path)

    def interactive(self, *args, **kwargs) -> None:
        """Starts an interactive session from within the class"""
        if kwargs:
            globals().update(kwargs)
        embed(
            globals(),
            locals(),
            history_filename=os.path.expanduser(f"~/.{self.title}_history"),
        )

    def show_help(self) -> None:
        """Print out the provided help text"""

        for cmd_name, cmd in self.commands.items():
            self.print(
                f"[cmd_name]{cmd_name}:[/cmd_name] [cmd_desc]{cmd.help_txt}[/cmd_desc]"
            )

    def print_prompt(self) -> None:
        """Prints the prompt message if defined"""

        if isinstance(self.init_prompt, list):
            for line in self.init_prompt:
                self.print(line)
        else:
            self.print(self.init_prompt)

    def run(self) -> None:
        """Initiates a REPL with the provided configuration"""

        completer = WordCompleter(
            self.get_cmd_names(), ignore_case=self.ignore_case
        )

        self.session = PromptSession(
            completer=completer,
            style=self.style,
            history=FileHistory(self.history),
            tempfile=self.temp_file,
            auto_suggest=SuggestFromLs(),
        )

        self.print_prompt()

        while True:
            try:
                user_input = self.session.prompt("> ", complete_while_typing=True)

                if user_input.lower() in ["help", "h"]:
                    self.show_help()
                elif user_input.lower() in self.exit_keywords:
                    self.print(f"[warn]Exiting REPL ({self.title})...[/warn]")
                    break
                else:
                    args = shlex.split(user_input)
                    if not args:
                        self.print("[warn][WARNING]: No command provided[/warn]")
                        continue

                    cmd = self.commands.get(args[0])

                    if not cmd:
                        self.print("[warn][WARNING]: Invalid command[/warn]")
                        continue

                    cmd_args = args[1:]
                    if cmd.command:
                        if cmd.parser:
                            if cmd_args and cmd_args[0] in [
                                "help",
                                "h",
                                "-h",
                                "--help",
                            ]:
                                cmd.parser.print_help()
                                continue

                            cmd.command(**vars(cmd.parser.parse_args(cmd_args)))
                        else:
                            if cmd.def_kwargs:
                                cmd.command(*cmd_args, **cmd.def_kwargs)
                            else:
                                cmd.command(*cmd_args)
                    else:
                        self.print(
                            "[warn][WARNING]: No function provided for command[/warn]"
                        )
            except (EOFError, KeyboardInterrupt):
                self.print(f"[warn]Exiting REPL ({self.title})...[/warn]")
                break
            except argparse.ArgumentError as e:
                self.print(f"[error]Error parsing arguments: {e}[/error]")
            except argparse.ArgumentTypeError as e:
                self.print(f"[error]Error parsing arguments: {e}[/error]")

        if self.parent:
            self.parent.print_prompt()


class SuggestFromLs(AutoSuggest):

    def get_suggestion(
        self, buffer: Buffer, document: Document
    ) -> Suggestion | None:
        files = os.listdir()

        # Consider only the last line for the suggestion.
        text = document.text.rsplit("\n", 1)[-1]
        split = text.split(" ", 1)
        if len(split) <= 1:
            return None
        text = split[1]
        if text.strip():
            for item in files:
                if item.lower().startswith(text.lower()):
                    return Suggestion(item[len(text) :])
        return None


@dataclass
class TestRepl(ReplBase):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_command("test_cmd", self.test_cmd, help_txt="Test command")

    def test_cmd(self) -> None:
        user_input = self.input("Testing prompt: ", suggestions=SuggestFromLs())
        self.print(user_input)


# endregion Classes


# region Functions

# endregion Functions
