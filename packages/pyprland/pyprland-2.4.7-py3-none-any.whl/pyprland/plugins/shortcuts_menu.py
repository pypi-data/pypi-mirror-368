"""Shortcuts menu."""

import asyncio
from typing import cast

from ..adapters.menus import MenuMixin
from ..common import CastBoolMixin, apply_filter, apply_variables, state
from .interface import Plugin


class Extension(CastBoolMixin, MenuMixin, Plugin):
    """Shows a menu with shortcuts."""

    # Commands

    async def run_menu(self, name: str = "") -> None:
        """[name] Shows the menu, if "name" is provided, will only show this sub-menu."""
        await self.ensure_menu_configured()
        options = self.config["entries"]
        if name:
            for elt in name.split("."):
                options = options[elt]

        def _format_title(label: str, obj: str | list) -> str:
            if isinstance(obj, str):
                suffix = self.config.get("command_end", "")
                prefix = self.config.get("command_start", "")
            else:
                suffix = self.config.get("submenu_end", "➜")
                prefix = self.config.get("submenu_start", "")

            return f"{prefix} {label} {suffix}".strip()

        while True:
            selection = name
            if isinstance(options, str):
                self.log.info("running %s", options)
                await self._run_command(options.strip(), state.variables)
                break
            if isinstance(options, list):
                self.log.info("interpreting %s", options)
                await self._handle_chain(options)
                break
            try:
                formatted_options = {_format_title(k, v): v for k, v in options.items()}
                if self.cast_bool(self.config.get("skip_single"), True) and len(formatted_options) == 1:
                    selection = next(iter(formatted_options.keys()))
                else:
                    selection = await self.menu.run(formatted_options, selection)
                options = formatted_options[selection]
            except KeyError:
                self.log.info("menu command canceled")
                break

    # Utils

    async def _handle_chain(self, options: list[str | dict]) -> None:
        """Handle a chain of special objects + final command string."""
        variables: dict[str, str] = state.variables.copy()
        autovalidate = self.cast_bool(self.config.get("skip_single"), True)
        for option in options:
            if isinstance(option, str):
                await self._run_command(option, variables)
            else:
                choices = []
                var_name = option["name"]
                if option.get("command"):  # use the option to select some variable
                    proc = await asyncio.create_subprocess_shell(option["command"], stdout=asyncio.subprocess.PIPE)
                    assert proc.stdout
                    await proc.wait()
                    option_array = (await proc.stdout.read()).decode().split("\n")
                    choices.extend([apply_variables(line, variables).strip() for line in option_array if line.strip()])
                elif option.get("options"):
                    choices.extend(apply_variables(txt, variables) for txt in option["options"])
                if len(choices) == 0:
                    await self.notify_info("command didn't return anything")
                    return

                if autovalidate and len(choices) == 1:
                    variables[var_name] = choices[0]
                else:
                    selection = await self.menu.run(choices, var_name)
                    variables[var_name] = apply_filter(selection, cast(str, option.get("filter", "")))
                    self.log.debug("set %s = %s", var_name, variables[var_name])

    async def _run_command(self, command: str, variables: dict[str, str]) -> None:
        """Run a shell `command`, optionally replacing `variables`.

        The command is run in a shell, and the variables are replaced using the `apply_variables` function.

        Args:
            command: The command to run.
            variables: The variables to replace in the command.
        """
        final_command = apply_variables(command, variables)
        self.log.info("Executing %s", final_command)
        await asyncio.create_subprocess_shell(final_command)
