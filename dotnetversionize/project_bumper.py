from pathlib import Path
import subprocess

from .common_definitions import XML_TAG_FILE_VERSION
from .increment_type import IncrementType
from .version_number import VersionNumber
from xml.etree import ElementTree as et

def _get_csprojs_to_bump(csproj_file_collection: list[Path]) -> list[Path]:
    """
    Returns the list of `*.csproj` files which should be bumped due to
    changes within their project directory.

    Args:
        csproj_file_collection (list[Path]): List of files to verify.

    Returns:
        list[Path]: List of `*.csproj` files to bump.
    """
    def file_needs_bumping(csproj_file: Path) -> bool:
        _command = f"git diff --quiet HEAD HEAD~1 -- {csproj_file.parent} --exit-code || exit 1"
        # If there are changes it will return then exit code = 1.
        _result = subprocess.run(_command.split())
        return _result.returncode == 1
    return list(filter(file_needs_bumping, csproj_file_collection))

def project_bumper(root_dir: Path, increment_type: IncrementType):
    """
    Bumps the given directory project version files if elligible.

    Args:
        root_dir (Path): Root directory containing project files to bump.
        increment_type (IncrementType): Increment to apply to all the projects to bump.
    """
    if increment_type == IncrementType.NONE:
        print("No increment to apply.")
        exit(code=0)

    _csproj_collection = list(root_dir.rglob("*.csproj"))
    _project_files_to_bump = _get_csprojs_to_bump(_csproj_collection)
    if not _project_files_to_bump:
        print("No projects found to bump.")
        exit(code=1)
        
    # Bump versions
    print("Bumping versions for:")
    _bump_mssgs = []
    # Get commit headers
    for _csproj_file in _project_files_to_bump:
        # Find the xml version number
        _xml_props = et.parse(_csproj_file)
        _attribute_to_replace = _xml_props.find(f".//{XML_TAG_FILE_VERSION}")
        _initial_value = _attribute_to_replace.text

        # Map xml version number
        _project_version = VersionNumber.from_tuple(tuple(map(int, _initial_value.split("."))))
        _project_version.bump(increment_type)

        # Set new value to xml
        _attribute_to_replace.text = str(_project_version)
        _xml_props.write(_csproj_file)

        # Add bump commit (partial) message.
        _bump_mssg = f"* {_csproj_file.parent.name} (\'{_initial_value}\' -> \'{_attribute_to_replace.text}\')"
        print(_bump_mssg)
        _bump_mssgs.append(_bump_mssg)

    # Commit all 'bumping' changes
    _bump_mssgs_str = "\n".join(_bump_mssgs)
    _command = ["git", "commit", "-am", f"bump({increment_type.name.lower()}): autobumping of project versions.", "-m", _bump_mssgs_str]
    _result = subprocess.run(_command)
    exit(code=_result.returncode)

