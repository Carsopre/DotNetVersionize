from .common_definitions import XML_TAG_FILE_VERSION, XML_TAG_VERSION, COMMIT_HEADER_RELEASE, COMMIT_HEADER_MERGE, COMMIT_HEADER_BUMP
from .increment_type import IncrementType
from .version_number import VersionNumber
from pathlib import Path
from xml.etree import ElementTree as et
import subprocess

def product_bumper(root_dir: Path, increment_type: IncrementType, latest_git_tag: str):
    """
    Bumps the given product directory to the next release if elligible.

    Args:
        root_dir (Path): Directory containing all the (sub-)products to be bumped.
        increment_type (IncrementType): Increment to apply to all the products to bump.
        latest_tag: Latest published git tag in format `vMAJOR.Minor.patch`.
    """
    if increment_type == IncrementType.NONE:
        print("No increment to apply.")
        exit(code=0)

    # For now we search directly for the `Directory.Build.props`
    _props_filename = "Directory.Build.props"
    _props_file = next(root_dir.rglob(_props_filename), None)
    if not _props_file:
        print(f"{_props_filename} not found in {root_dir}.")
        exit(code=1)
 
    # Expected format is `vMAJOR.Minor.patch`
    # This step was already done, but for now we leave it as it is.
    _product_version = VersionNumber.from_tag(latest_git_tag)
    _product_version.bump(increment_type)

    # Bump
    # For now we do an automatic Minor bump
    _xml_parser = et.XMLParser(target=et.TreeBuilder(insert_comments=True))
    _xml_props = et.parse(_props_file, _xml_parser)
    _tags_to_bump = [XML_TAG_FILE_VERSION, XML_TAG_VERSION]
    _commit_description_mssgs = []
    for _tag_to_bump in _tags_to_bump:
        _attribute_to_replace = _xml_props.find(f".//{_tag_to_bump}")
        _bumped_version = _product_version.generate_bumped_version(_attribute_to_replace.text, args.release_candidate)
        if not _bumped_version:
            print(f"Version already bumped for tag {_tag_to_bump}. Automatic bump not possible, try manually.")
            exit(code=1)

        # We can't get the release candidate from a tag (we do not publish them as of now)
        # so we can update it here.
        if args.release_candidate:
            _product_version.release_candidate = _bumped_version.release_candidate
        _commit_description = f"* bump({increment_type.name.lower()}): {_tag_to_bump} {_attribute_to_replace.text} -> {_bumped_version}"
        _commit_description_mssgs.append(_commit_description)
        _attribute_to_replace.text = str(_bumped_version)
    _xml_props.write(_props_file)
    
    # Commit message
    # Last commit message (required to generate the bump one)
    _version_tag = _product_version.as_git_tag()
    _release_title = ""
    if args.release_title:
        _release_title = args.release_title
    else:
        # -3 because, merge-commit, bump-commit, last "content" commit
        _last_relevant_commits = _get_commit_list("-3")
        def valid_commit_header(commit_mssg: str) -> bool:
            _normalized = commit_mssg.lower().strip()
            if _normalized.startswith(COMMIT_HEADER_RELEASE.lower()):
                return True
            if _normalized.startswith(COMMIT_HEADER_MERGE.lower()) or _normalized.startswith(COMMIT_HEADER_BUMP.lower()):
                return False
            return False
        _release_title = next(filter(valid_commit_header, _last_relevant_commits), "Untitled release").split(":")[-1]
        
    _bump_context = "release-candidate" if args.release_candidate else "release"
    _commit_mssg = f"bump({_bump_context}): [{_version_tag}] - {_release_title}"
    _commit_description = "\n".join(_commit_description_mssgs)
    
    _command = ["git", "commit", "-am", f"{_commit_mssg}", "-m", f"{_commit_description}"]
    _result = subprocess.run(_command)

    if args.release_candidate:
        print("Do not forget to push all your changes: 'git push'.")
        exit(code=_result.returncode)

    # Create new tag
    _command = f"git tag {_version_tag}"
    _result = subprocess.run(_command.split())
    if _result.returncode != 0:
        print(f"Error while creating tag {_version_tag}")
        exit(code=1)
    print(f"Generated new tag {_version_tag}")
    print("Do not forget to push all your changes: 'git push --tags && git push'.")
    exit(code=_result.returncode)
