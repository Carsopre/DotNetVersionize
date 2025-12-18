from dataclasses import dataclass

from .common_definitions import VERSION_SUFFIX_RELEASE_CANDIDATE
from .increment_type import IncrementType


@dataclass
class VersionNumber:
    """
    Dataclass to represent the `MAJOR`, `Minor`, `patch` version numbers and some useful
    methods to map and bump them.
    """

    major: int
    minor: int
    patch: int
    release_candidate: int = 0
    suffix: str = ""

    def __str__(self):
        _suffix = self.suffix
        if self.release_candidate > 0:
            _suffix = f"{VERSION_SUFFIX_RELEASE_CANDIDATE}.{self.release_candidate}"
        return f"{self.major}.{self.minor}.{self.patch}{_suffix}"

    def as_git_tag(self) -> str:
        """
        Generates a git tag format string.

        Returns:
            str: Version number in git format.
        """
        return f"v{str(self)}"

    @property
    def is_release_candidate(self) -> bool:
        """
        Verifies whether this version correspond to one holding a release candidate.

        Returns:
            bool: Is a release candidate version.
        """
        return (
            self.suffix.startswith(VERSION_SUFFIX_RELEASE_CANDIDATE)
            or self.release_candidate > 0
        )

    @classmethod
    def from_tuple(cls, version_numbers: tuple[int, int, int]):
        """
        Generates a `VersionNumber` instance by providing a tuple of at least three numbers.
        These are then mapped following the Semantic Versioning convention https://semver.org/.

        Args:
            version_numbers (tuple[int, int, int]): Version numbers MAJOR.Minor.patch

        Returns:
            VersionNumber: Mapped instance
        """
        if not version_numbers or len(version_numbers) < 3:
            raise ValueError("A version number is composed of at least three values.")

        return cls(
            major=version_numbers[0], minor=version_numbers[1], patch=version_numbers[2]
        )

    @classmethod
    def from_tag(cls, version_tag: str):
        """
        This class method helps us correctly  mapping tags that may contain
        a suffix, for instance for pre-releases such as `v0.6.0-alpha` or
        `v0.6.0alpha23` which should just take the first `0` as a patch.

        Args:
            version_tag (str): Tag to parse.

        Returns:
            VersionNumber: Resulting mapped instance.
        """
        _parts = version_tag.split("v")[-1].split(".")

        _patch_str_list = [
            _patch_digit
            for _patch_digit in takewhile(lambda x: x.isnumeric(), _parts[2])
        ]
        _suffix = ""
        if len(_patch_str_list) < len(_parts[2]):
            _suffix = _parts[2][len(_patch_str_list) :]

        _mapped_version = cls(
            major=int(_parts[0]),
            minor=int(_parts[1]),
            patch=int("".join(_patch_str_list)),
            suffix=_suffix,
        )

        if VERSION_SUFFIX_RELEASE_CANDIDATE in version_tag:
            _mapped_version.release_candidate = int(
                version_tag.split(f"{VERSION_SUFFIX_RELEASE_CANDIDATE}.")[-1]
            )
            _mapped_version.suffix = ""

        return _mapped_version

    def generate_bumped_version(
        self, product_version: str, as_release_candidate: bool
    ) -> VersionNumber | None:
        """
        Generates a bumped version from a product compared to this instance.
        """
        _pv = VersionNumber.from_tag(product_version)
        _rc_number = 0 if not as_release_candidate else _pv.release_candidate + 1
        if not _pv.is_release_candidate:
            # Check if we can bump or the product's version is already higher than us,
            # if that's the case we do not generate a new bumped version.
            if self.major < _pv.major:
                # Cannot bump when major version is greater.
                return None
            elif self.major == _pv.major:
                if self.minor < _pv.minor:
                    return None
                if self.minor == _pv.minor and self.patch <= _pv.patch:
                    return None

        _pv.major = self.major
        _pv.minor = self.minor
        _pv.patch = self.patch
        _pv.release_candidate = _rc_number
        _pv.suffix = ""

        return _pv

    def bump(self, increment_type: IncrementType) -> None:
        """
        Increment this instance's version number.

        Args:
            increment_type (IncrementType): Increment type.
        """
        match increment_type:
            case IncrementType.MAJOR:
                self.major += 1
                self.minor = 0
                self.patch = 0
                self.suffix = ""
            case IncrementType.MINOR:
                self.minor += 1
                self.patch = 0
                self.suffix = ""
            case IncrementType.PATCH:
                self.patch += 1
                self.suffix = ""
            case _:
                print("No increment to apply")
