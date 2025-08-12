import os
from contextlib import suppress

from pathspec import PathSpec


def delete_out_of_scope_files(git_ignore: list[str], repo_path: str) -> None:
    # Compute what files should be deleted according to the scope rules
    spec: PathSpec = PathSpec.from_lines("gitwildmatch", git_ignore)
    for match in spec.match_tree(repo_path):
        if match.startswith(".git/"):
            continue

        file_path = os.path.join(repo_path, match)
        if os.path.isfile(file_path):
            with suppress(FileNotFoundError):
                os.unlink(file_path)

    # remove empty directories
    for root, dirs, _ in os.walk(repo_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # noqa: PTH208
                os.rmdir(dir_path)
