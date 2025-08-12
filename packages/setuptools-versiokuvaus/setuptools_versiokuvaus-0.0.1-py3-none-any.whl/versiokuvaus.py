import os
from pathlib import Path

from git import InvalidGitRepositoryError, Repo


def kirjoita_versiokuvaus(cmd, basename, filename):
  try:
    repo = Repo(Path.cwd())
  except InvalidGitRepositoryError:
    return

  argname = os.path.splitext(basename)[0]
  cmd.write_or_delete_file(argname, filename, repo.head.commit.message)
