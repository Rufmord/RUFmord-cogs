from AAA3A_utils import Cog, CogsUtils, Menu  # isort:skip
from redbot.core import commands  # isort:skip
from redbot.core.bot import Red  # isort:skip
from redbot.core.i18n import Translator, cog_i18n  # isort:skip
import discord  # isort:skip

import inspect
import io
import os
import re
import textwrap
import typing
from os import listdir
from pathlib import Path

from redbot.core import data_manager
from redbot.core.utils.chat_formatting import box, pagify

# Credits:
# General repo credits.

# Initial purpose of this cog is to allow server users to print file structure of music directories.

_: Translator = Translator("ListFiles", __file__)


@cog_i18n(_)
class ListFiles(Cog):
    """A cog to get a file and replace it from its path from Discord!

    ⚠️ This cog can be very dangerous, since it allows direct read/write/delete of files on the bot’s machine, considering the fact that reading the wrong file can expose sensitive information like tokens and deleting the wrong file can corrupt the bot or the system entirely.
    """

    @commands.is_owner()
    @commands.hybrid_group(aliases=["ls"])
    async def listfiles(self, ctx: commands.Context) -> None:
        """Commands group to get a file and replace it from its path."""
        pass


    @listfiles.command()
    @listfiles.aliases(["dir", "."])
    async def listdir(self, ctx: commands.Context, *, path: str) -> None:
        """List all files/directories of a directory from its path."""
        path = Path(CogsUtils.replace_var_paths(path, reverse=True))
        if not path.exists():
            raise commands.UserFeedbackCheckFailure(
                _("This directory cannot be found on the host machine.")
            )
        if not path.is_dir():
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a file, not a directory.")
            )
        message = ""
        files = listdir(str(path))
        files = sorted(files, key=lambda file: (path / file).is_dir(), reverse=True)
        for file in files:
            path_file = path / file
            if path_file.is_file():
                message += "\n" + f"- [FILE] {file}"
            elif path_file.is_dir():
                message += "\n" + f"- [DIR] {file}"
        message = CogsUtils.replace_var_paths(message)
        await Menu(pages=message, lang="ini").start(ctx)

    @listfiles.command()
    @listfiles.aliases(["tree"])
    async def treedir(self, ctx: commands.Context, *, path: str) -> None:
        """Make a tree with all files/directories of a directory from its path."""
        path = Path(CogsUtils.replace_var_paths(path, reverse=True))
        if not path.exists():
            raise commands.UserFeedbackCheckFailure(
                _("This directory cannot be found on the host machine.")
            )
        if not path.is_dir():
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a file, not a directory.")
            )

        def tree(base):
            lines = []
            files = sorted(base.iterdir(), key=lambda s: s.name.lower())
            for num, path in enumerate(files, start=1):
                prefix = "└── " if num == len(files) else "├── "
                if path.name.startswith(".") or {"venv", "__pycache__"} & {
                    p.name for p in path.parents
                }:
                    continue
                lines.append(prefix + path.name)
                if path.is_dir():
                    indent = "   " if num == len(files) else "|   "
                    lines.append(textwrap.indent(tree(path), prefix=indent))
            return "\n".join(lines)

        message = CogsUtils.replace_var_paths(tree(path))
        await Menu(pages=message, lang="ini").start(ctx)
