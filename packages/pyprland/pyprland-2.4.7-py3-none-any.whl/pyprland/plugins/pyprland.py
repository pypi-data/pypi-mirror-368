"""Not a real Plugin - provides some core features and some caching of commonly requested structures."""

import json

from ..common import state
from ..types import VersionInfo
from .interface import Plugin

DEFAULT_VERSION = VersionInfo(9, 9, 9)


class Extension(Plugin):
    """Internal built-in plugin allowing caching states and implementing special commands."""

    async def init(self) -> None:
        """Initialize the plugin."""
        state.active_window = ""
        # Examples:
        # "tag": "v0.40.0-127-g4e42107d", (for git)
        # "tag": "v0.40.0", (stable)
        version_str = ""
        auto_increment = False
        try:
            version_info: None | dict[str, str | bool | list] = await self.hyprctl_json("version")
            assert isinstance(version_info, dict)
        except json.JSONDecodeError:
            self.log.exception("Fail to parse hyprctl version")
            await self.notify_error("Error: 'hyprctl version' didn't print valid data")
        else:
            _tag = version_info.get("tag")
            if _tag:
                assert isinstance(_tag, str)
                version_str = _tag.split("-", 1)[0]
                if len(version_str) < len(_tag):
                    auto_increment = True
            else:
                version_str = version_info.get("version")

        if version_str:
            try:
                self.__set_hyprland_version(version_str[1:] if version_str.startswith("v") else version_str, auto_increment)
            except Exception:  # pylint: disable=broad-except
                self.log.exception('Fail to parse version tag "%s"', version_str)
                await self.notify_error(f"Failed to parse hyprctl version tag: {version_str}")
                version_str = ""

        if not version_str:
            self.log.error("Fail to parse version information: %s - using default", version_info)
            state.hyprland_version = DEFAULT_VERSION

        state.active_workspace = (await self.hyprctl_json("activeworkspace"))["name"]
        monitors = await self.hyprctl_json("monitors")
        state.monitors = [mon["name"] for mon in monitors]
        state.active_monitor = next(mon["name"] for mon in monitors if mon["focused"])

    async def event_monitoradded(self, name: str) -> None:
        """Track monitor."""
        state.monitors.append(name)

    async def event_monitorremoved(self, name: str) -> None:
        """Track monitor."""
        try:
            state.monitors.remove(name)
        except ValueError:
            self.log.warning("Monitor %s not found in state - can't be removed", name)

    async def on_reload(self) -> None:
        """Reload the plugin."""
        state.variables = self.config.get("variables", {})
        version_override = self.config.get("hyprland_version")
        if version_override:
            self.__set_hyprland_version(version_override)

    async def event_activewindowv2(self, addr: str) -> None:
        """Keep track of the focused client."""
        if not addr:
            self.log.debug("no active window")
            state.active_window = ""
        else:
            state.active_window = "0x" + addr
            self.log.debug("active_window = %s", state.active_window)

    async def event_workspace(self, workspace: str) -> None:
        """Track the active workspace."""
        state.active_workspace = workspace
        self.log.debug("active_workspace = %s", state.active_workspace)

    async def event_focusedmon(self, mon: str) -> None:
        """Track the active workspace."""
        state.active_monitor, state.active_workspace = mon.rsplit(",", 1)
        self.log.debug("active_monitor = %s", state.active_monitor)

    def set_commands(self, **cmd_map) -> None:
        """Set some commands, made available as run_`name` methods."""
        for name, fn in cmd_map.items():
            setattr(self, f"run_{name}", fn)

    def __set_hyprland_version(self, version_str: str, auto_increment: bool = False) -> None:
        """Set the hyprland version."""
        split_version = [int(i) for i in version_str.split(".")[:3]]
        if auto_increment:
            split_version[-1] += 1
        state.hyprland_version = VersionInfo(*split_version)
