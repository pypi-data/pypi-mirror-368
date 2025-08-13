from collections.abc import Collection, Mapping
from functools import cache
from importlib.metadata import EntryPoint, entry_points, version

from .plugin import Plugin


def _get_installed_plugin(
    entry_point: EntryPoint, /, *, expected_version: str
) -> Plugin:
    assert entry_point.dist
    plugin_package_name = entry_point.dist.name
    plugin_version = version(plugin_package_name)

    assert plugin_version == expected_version, (
        f"This version of Atoti only supports {plugin_package_name} v{expected_version} but got v{plugin_version}."
    )

    plugin_class = entry_point.load()
    plugin = plugin_class()

    if not isinstance(plugin, Plugin):
        raise TypeError(f"Unexpected plugin type: {type(plugin)}.")

    return plugin


@cache
def _get_all_installed_plugins() -> Mapping[str, Plugin]:
    expected_version = version("atoti-client")
    plugin_entry_points = entry_points(group="atoti.plugins")
    return {
        entry_point.name: _get_installed_plugin(
            entry_point, expected_version=expected_version
        )
        for entry_point in plugin_entry_points
    }


def get_installed_plugins(*, keys: Collection[str] | None = None) -> dict[str, Plugin]:
    return {
        key: plugin
        for key, plugin in _get_all_installed_plugins().items()
        if keys is None or key in keys
    }
