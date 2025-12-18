import pytest

from dotnetversionize.increment_type import IncrementType


class TestIncrementType:
    def test_increment_type(self):

        assert IncrementType.PATCH.name == "PATCH"
        assert IncrementType.PATCH.value == 2

        assert IncrementType.MINOR.name == "MINOR"
        assert IncrementType.MINOR.value == 1

        assert IncrementType.MAJOR.name == "MAJOR"
        assert IncrementType.MAJOR.value == 0

        assert IncrementType.NONE.name == "NONE"
        assert IncrementType.NONE.value == 99

    @pytest.mark.parametrize(
        "commit_message, expected_increment",
        [
            pytest.param(
                "feat: correct typo", IncrementType.MINOR, id="minor increment"
            ),
            pytest.param(
                "!fix: correct typo", IncrementType.MAJOR, id="major increment"
            ),
            pytest.param(
                "fix: correct typo", IncrementType.PATCH, id="patch increment"
            ),
            pytest.param(
                "chore: update dependencies", IncrementType.NONE, id="no increment"
            ),
        ],
    )
    def test_increment_type_detection(
        self, commit_message: str, expected_increment: IncrementType
    ):
        assert (
            IncrementType.detect_commit_increment(commit_message) == expected_increment
        )
