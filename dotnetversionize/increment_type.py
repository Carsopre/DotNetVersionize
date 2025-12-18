from __future__ import annotations


from .common_definitions import (
    COMMIT_HEADER_BREAKING,
    COMMIT_HEADER_FEAT,
    COMMIT_HEADER_FIX,
)
from enum import Enum


class IncrementType(Enum):
    """
    Definition of our "built-in" increment types, following
    the Semantic Versioning convention https://semver.org/ .

    By definition, a lower `IncrementType` enum value means that said increment
    has higher priority than the rest. So `MAJOR` > `MINOR` > `PATCH` despite `0<1<2`.
    However, this definition helps us extend, if needed, the enum definition with version
    parts lower than patch such as 'pre-releases' ( `MAJOR.MINOR.PATCH.pre-release`).
    """

    MAJOR = 0
    MINOR = 1
    PATCH = 2
    NONE = 99

    @staticmethod
    def detect_commit_increment(commit_mssg: str) -> IncrementType:
        """
        Maps a commit message to a valid increment type following the conventional
        commits standard.
        Based on https://www.conventionalcommits.org/en/v1.0.0/

        Args:
            commit_mssg (str): Message to map.

        Returns:
            IncrementType: Resulting mapped increment type.
        """
        _header = commit_mssg.split(":", maxsplit=1)[0]

        # BREAKING CHANGE / '!' = MAJOR
        if "!" in _header.split(":", maxsplit=1)[0] or _header.startswith(
            COMMIT_HEADER_BREAKING
        ):
            return IncrementType.MAJOR
        else:
            # feat change = Minor
            if _header.startswith(COMMIT_HEADER_FEAT):
                return IncrementType.MINOR
            # fix change = patch
            if _header.startswith(COMMIT_HEADER_FIX):
                return IncrementType.PATCH
        return IncrementType.NONE

    @staticmethod
    def detect_commit_list_increment(commit_mssgs: list[str]) -> IncrementType:
        """
        Detects what kind of increment should be applied following the conventional
        commits standard.
        Based on https://www.conventionalcommits.org/en/v1.0.0/

        Args:
            commit_mssgs (list[str]): List of commit messages to analyze.

        Returns:
            IncrementType: Built-in increment corresponding to the provided commit messages.
        """
        # Map headers to increment type:
        _min_increment = min(
            set(
                (
                    map(
                        lambda x: IncrementType.detect_commit_increment(x).value,
                        commit_mssgs,
                    )
                )
            )
        )
        _found_increment = IncrementType(_min_increment)
        print(f"'{_found_increment.name}' increment detected.")
        return _found_increment
