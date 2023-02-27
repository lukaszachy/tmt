import shutil
from typing import List, Optional

import tmt
from tmt.utils import Path

from . import Library, LibraryError, LibraryIdentifierType


class File(Library):
    """
    Required files

    Takes care of copying required files for specific test or library,
    more details here:
    https://tmt.readthedocs.io/en/latest/spec/tests.html#require

    Optional 'parent' object inheriting from tmt.utils.Common can be
    provided in order to share the cache of already fetched libraries.

    The following attributes are available in the object:

    repo ........ library prefix (git repository name or nick if provided)
    pattern ..... filename paths and regexes which need to be copied
    """

    def __init__(
            self,
            *,
            identifier: LibraryIdentifierType,
            parent: Optional[tmt.utils.Common] = None,
            logger: tmt.log.Logger,
            source_location: Path,
            target_location: Path) -> None:
        super().__init__(parent=parent, logger=logger)

        self.identifier = identifier
        self.format: str = identifier.type if (
            hasattr(identifier, 'type') and isinstance(identifier.type, str)) else 'file'
        self.repo: Path = Path(target_location.name)
        self.name: Path = Path("/files")
        self.pattern: List[str] = identifier.pattern if hasattr(identifier, 'pattern') else []
        self.source_location: Path = source_location
        self.target_location: Path = target_location

    def fetch(self) -> None:
        """ Copy the files over to target location """
        self.parent.debug(
            'Searching for patterns: '
            f'{", ".join(pattern for pattern in self.pattern if pattern)} '
            f'in directory {str(self.source_location)}')
        files: List[Path] = tmt.utils.filter_paths(
            self.source_location, self.pattern)
        if not files:
            self.parent.debug('No files found')
            raise LibraryError
        self.parent.debug(f'Found paths: {", ".join([str(f) for f in files])}')
        for path in files:
            assert path is not None  # narrow type
            local_path = path.relative_to(self.source_location).parent
            target_path = Path(self.target_location) / local_path
            if path.is_dir():
                tmt.utils.copytree(path, target_path, dirs_exist_ok=True)
            else:
                target_path.mkdir(exist_ok=True)
                target_path = target_path / path.name
                if not target_path.exists():
                    shutil.copyfile(path, target_path)
