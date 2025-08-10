"""Plugin template."""

import asyncio
import os.path
import random
from collections.abc import AsyncIterator

from ..aioops import ailistdir
from ..common import CastBoolMixin, apply_variables, prepare_for_quotes, state
from .interface import Plugin


def expand_path(path: str) -> str:
    """Expand the path."""
    return os.path.expanduser(os.path.expandvars(path))


async def get_files_with_ext(path: str, extensions: list[str], recurse: bool = True) -> AsyncIterator[str]:
    """Return files matching `extension` in given `path`. Can optionally `recurse` subfolders.."""
    for fname in await ailistdir(path):
        ext = fname.rsplit(".", 1)[-1]
        full_path = os.path.join(path, fname)
        if ext.lower() in extensions:
            yield full_path
        elif recurse and os.path.isdir(full_path):
            async for v in get_files_with_ext(full_path, extensions, True):
                yield v


class Extension(CastBoolMixin, Plugin):
    """Manages the background image."""

    default_image_ext: set[str] | list[str] = {"png", "jpg", "jpeg"}
    image_list: list[str] = []
    running = True
    proc: list = []
    loop = None

    next_background_event = asyncio.Event()
    cur_image = ""
    _paused = False

    async def on_reload(self) -> None:
        """Re-build the image list."""
        cfg_path = self.config["path"]
        paths = [expand_path(cfg_path)] if isinstance(cfg_path, str) else [expand_path(p) for p in cfg_path]
        extensions = self.config.get("extensions", self.default_image_ext)

        self.image_list = [
            os.path.join(path, fname)
            for path in paths
            async for fname in get_files_with_ext(path, extensions, recurse=self.cast_bool(self.config.get("recurse")))
        ]

        # Start the main loop if it's the first load of the config
        if self.loop is None:
            self.loop = asyncio.create_task(self.main_loop())

    async def exit(self) -> None:
        """Terminates gracefully."""
        self.running = False
        if self.loop:
            self.loop.cancel()
        await self.terminate()

    async def event_monitoradded(self, _: str) -> None:
        """When a new monitor is added, set the background."""
        self.next_background_event.set()

    def select_next_image(self) -> str:
        """Return the next image (random is supported for now)."""
        choice = random.choice(self.image_list)
        if choice == self.cur_image:
            choice = random.choice(self.image_list)
        self.cur_image = choice
        return choice

    async def _run_one(self, template: str, values: dict[str, str]) -> None:
        """Run one command."""
        cmd = apply_variables(template, values)
        self.log.info("Running %s", cmd)
        self.proc.append(await asyncio.create_subprocess_shell(cmd))

    async def main_loop(self) -> None:
        """Run the main plugin loop in the 'background'."""
        self.proc = []
        unique = self.config.get("unique", False)
        variables = state.variables.copy()

        while self.running:
            if not self._paused:
                self.next_background_event.clear()

                # Define the command template based on the 'unique' flag
                cmd_template = self.config.get(
                    "command",
                    ('swaybg -o [output] -m fill -i "[file]"' if unique else 'swaybg -m fill -i "[file]"'),
                )

                if unique:
                    monitors = await self.hyprctl_json("monitors")
                    old_filename = None
                    for monitor in monitors:
                        filename = prepare_for_quotes(self.select_next_image())
                        while filename == old_filename:
                            filename = prepare_for_quotes(self.select_next_image())
                        variables.update({"file": filename, "output": monitor["name"]})
                        await self._run_one(cmd_template, variables)
                else:
                    filename = self.select_next_image().replace('"', '\\"')
                    variables.update({"file": filename})
                    await self._run_one(cmd_template, variables)

                await asyncio.sleep(1)  # wait for the command(s) to start

                # check if the command failed
                for proc in self.proc:
                    if proc.returncode:
                        await self.notify_error("wallpaper command failed")

            interval = asyncio.sleep(60 * self.config.get("interval", 10) - 1)
            await asyncio.wait(
                [
                    asyncio.create_task(interval),
                    asyncio.create_task(self.next_background_event.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            await self.terminate()

    async def terminate(self) -> None:
        """Exit existing process if any."""
        if self.proc:
            for proc in self.proc:
                if proc.returncode is None:
                    proc.terminate()
                await proc.wait()
        self.proc[:] = []

    async def run_wall(self, arg: str) -> None:
        """<next|clear> skip the current background image or stop displaying it."""
        if arg.startswith("n"):
            self._paused = False
            self.next_background_event.set()
        elif arg.startswith("c"):
            clear_command = self.config.get("clear_command")
            if clear_command:
                # call clear_command subprocess
                proc = await asyncio.create_subprocess_shell(clear_command)
                # wait for it to finish
                await proc.wait()
            else:
                self._paused = True
                await self.terminate()
