from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, final

from _atoti_core import Plugin
from typing_extensions import override

from ._resources_directory import RESOURCES_DIRECTORY

if TYPE_CHECKING:
    import atoti as tt  # pylint: disable=nested-import,undeclared-dependency


@final
class ObservabilityPlugin(Plugin):
    @override
    def session_config_hook(
        self,
        session_config: tt.SessionConfig,
    ) -> tt.SessionConfig:
        if not any(
            option.startswith("-javaagent") for option in session_config.java_options
        ):
            session_config = replace(
                session_config,
                java_options=[
                    *session_config.java_options,
                    "-javaagent:"
                    + str(
                        RESOURCES_DIRECTORY / "opentelemetry-javaagent.jar"
                    ),  # This java agent is used for opentelemetry version 1.44.1, it needs to be updated when the version is updated.
                ],
            )
        return replace(
            session_config,
            extra_jars=[
                *session_config.extra_jars,
                RESOURCES_DIRECTORY / "plugin.jar",
            ],
        )

    @property
    @override
    def _key(self) -> str | None:
        return "observability"
