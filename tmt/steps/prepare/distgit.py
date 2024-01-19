import dataclasses
from typing import Any, List, Optional

import tmt
import tmt.log
import tmt.steps
import tmt.steps.prepare
import tmt.utils
from tmt.steps.provision import Guest
from tmt.utils import Command, Path, field

PREPARE_WRAPPER_FILENAME = 'tmt-prepare-wrapper.sh'


@dataclasses.dataclass
class ExtractDistGitData(tmt.steps.prepare.PrepareStepData):
    source_dir: Optional[Path] = field(
        default=None,
        option='--source-dir',
        normalize=tmt.utils.normalize_path,
        exporter=lambda value: str(value) if isinstance(value, Path) else None)
    phase_name: str = field(default_factory=str, option='--phase-name')
    order: int = 60
    install_builddeps: bool = field(
        default=False,
        option="--install-builddeps",
        is_flag=True,
        help="Install package build dependencies",
        )
    require: List['tmt.base.DependencySimple'] = field(
        default_factory=list,
        option="--require",
        metavar='PACKAGE',
        multiple=True,
        help='Additional required package to be present before sources are prepared',
        # *simple* requirements only
        normalize=lambda key_address, value, logger: tmt.base.assert_simple_dependencies(
            tmt.base.normalize_require(key_address, value, logger),
            "'require' can be simple packages only",
            logger),
        serialize=lambda packages: [package.to_spec() for package in packages],
        unserialize=lambda serialized: [
            tmt.base.DependencySimple.from_spec(package)
            for package in serialized
            ]
        )


@tmt.steps.provides_method('distgit')
class PrepareExtractDistGit(tmt.steps.prepare.PreparePlugin[ExtractDistGitData]):
    """
    Companion to the discover-dist-git

    """

    _data_class = ExtractDistGitData

    def __init__(
            self,
            *,
            discover: Optional['tmt.steps.discover.DiscoverPlugin'] = None,
            **kwargs: Any):
        super().__init__(**kwargs)
        self.discover: discover

    def go(
            self,
            *,
            guest: 'Guest',
            environment: Optional[tmt.utils.EnvironmentType] = None,
            logger: tmt.log.Logger) -> None:
        """ Prepare the guests """

        super().go(guest=guest, environment=environment, logger=logger)

        environment = environment or {}

        # Install packages required for this plugin to work and additional required packages
        additional_require = [*self.get('require', []), 'rpm-build']

        data = tmt.steps.prepare.install.PrepareInstallData(
            package=additional_require,
            name='unused',
            how='unused'
            )
        prepare_install = tmt.steps.prepare.install.PrepareInstall(
            step=self.parent,
            data=data,
            workdir=None,
            logger=self._logger,
            )
        # FIXME -- use correct guest.facts
        installer = tmt.steps.prepare.install.InstallDnf(
            logger=logger, parent=prepare_install, guest=guest)
        installer.install()

        # TODO
        # install_build_require: bool = self.get('install_builddeps')
        # rpmbuild -br spec
        # dnf-build-dep <spec from previous step>

        source_dir = self.data.source_dir
        assert source_dir

        try:
            spec_name = next(Path(source_dir).glob('*.spec')).name
        except StopIteration:
            raise tmt.utils.PrepareError(f"No '*.spec' file found in '{source_dir}'")

        cmd = Command(
            "rpmbuild", "-bp", spec_name, "--nodeps",
            "--define", f'_sourcedir {source_dir}',
            "--define", f'_builddir {source_dir}'
            )

        try:
            guest.execute(command=cmd,
                          cwd=source_dir,
                          )
        except tmt.utils.RunError as error:
            raise tmt.utils.PrepareError("Unable to 'rpmbuild -bp'", causes=[error])

        # Make sure to pull back sources ...
        guest.pull(source_dir)

        # When discover is not set we do not run anything else
        if self.discover is None:
            return
        raise NotImplementedError
