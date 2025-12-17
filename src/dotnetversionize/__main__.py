
# region ARG PARSER
# Initialize parser
from pathlib import Path

from .git_interface import get_commit_list, get_latest_tag
from .increment_type import IncrementType
import argparse

from .product_bumper import product_bumper
from .project_bumper import project_bumper


parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument(
    "--release",
    help="Generate a release bump.",
    action="store_true")
parser.add_argument(
    "--release-title", 
    nargs='?', 
    help="Adds a title to a release, has no use otherwise")
parser.add_argument(
    "--release-candidate", 
    help="Creates, or bumps, a release candidate version. The follow-up --release will just remove the suffix .",
    action="store_true")
parser.add_argument(
    "--increment",
    choices=[IncrementType.MAJOR.name, IncrementType.MINOR.name, IncrementType.PATCH.name],
    help="Manually specify what increment should be applied, can be combined with other arguments.")
args = parser.parse_args()

if __name__ == '__main__':
    _root_dir = Path(__file__).parent

    if args.release or args.release_candidate:
        _latest_tag = get_latest_tag()
        _increment_type = IncrementType.detect_commit_list_increment(get_commit_list(_latest_tag)) if not args.increment else IncrementType[args.increment]
        if(_increment_type == IncrementType.NONE):
            print("No increment to apply.")
            exit(code=0)
        product_bumper(_root_dir, _increment_type, _latest_tag)
    else:
        _increment_type = IncrementType.detect_commit_increment(get_commit_list("-1")[-1]) if not args.increment else IncrementType[args.increment]
        if(_increment_type == IncrementType.NONE):
            print("No increment to apply.")
            exit(code=0)
        project_bumper(_root_dir.joinpath("src"), _increment_type)
