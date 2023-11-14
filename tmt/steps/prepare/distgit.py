import dataclasses
from typing import Any, Dict, List, Optional, cast

import fmf

import tmt
import tmt.log
import tmt.steps
import tmt.steps.prepare
import tmt.utils
from tmt.steps.provision import Guest
from tmt.utils import ShellScript, field, Command

PREPARE_WRAPPER_FILENAME = 'tmt-prepare-wrapper.sh'


@dataclasses.dataclass
class DistGitData(tmt.steps.prepare.PrepareStepData):
    script: List[ShellScript] = field(
        default_factory=list,
        option=('-s', '--script'),
        multiple=True,
        metavar='SCRIPT',
        help='Shell script to be executed. Can be used multiple times.',
        normalize=tmt.utils.normalize_shell_script_list,
        serialize=lambda scripts: [str(script) for script in scripts],
        unserialize=lambda serialized: [ShellScript(script) for script in serialized]
        )

    # ignore[override] & cast: two base classes define to_spec(), with conflicting
    # formal types.
    def to_spec(self) -> Dict[str, Any]:  # type: ignore[override]
        data = cast(Dict[str, Any], super().to_spec())
        data['script'] = [str(script) for script in self.script]

        return data


@tmt.steps.provides_method('distgit')
class PrepareShell(tmt.steps.prepare.PreparePlugin[DistGitData]):
    """
    Companion to the discover-dist-git

    """

    _data_class = DistGitData

    def go(
            self,
            *,
            guest: 'Guest',
            environment: Optional[tmt.utils.EnvironmentType] = None,
            logger: tmt.log.Logger) -> None:
        """ Prepare the guests """
        super().go(guest=guest, environment=environment, logger=logger)

        environment = environment or {}


        # Install build require
        install_build_require: bool = self.get('install-build-require')

        if install_build_require:
        ## rpmbuild --define '_topdir $(TMP)' -br tmt.spec || sudo dnf builddep -y $(TMP)/SRPMS/tmt-*buildreqs.nosrc.rpm
            Command("rpmbuild", "--define", f"_topdir {XX}", "-br", "{SPEC}" )
        


        # Run rpmbuild -bp
        Command("rpmbuild", "-bp", ) #NODEPS
        # Pull sources
        # Re-discover for how: fmf (it should asked for it)

        # Give a short summary
        scripts: List[tmt.utils.ShellScript] = self.get('script')
        overview = fmf.utils.listed(scripts, 'script')
        logger.info('overview', f'{overview} found', 'green')

        workdir = self.step.plan.worktree
        assert workdir is not None  # narrow type

        if not self.is_dry_run:
            topology = tmt.steps.Topology(self.step.plan.provision.guests())
            topology.guest = tmt.steps.GuestTopology(guest)

            # Since we do not have the test data dir at hand, we must make the topology
            # filename unique on our own, and include the phase name and guest name.
            filename_base = f'{tmt.steps.TEST_TOPOLOGY_FILENAME_BASE}-{self.safe_name}-{guest.safe_name}'  # noqa: E501

            environment.update(
                topology.push(
                    dirpath=workdir,
                    guest=guest,
                    logger=logger,
                    filename_base=filename_base))

        prepare_wrapper_filename = f'{PREPARE_WRAPPER_FILENAME}-{self.safe_name}-{guest.safe_name}'
        prepare_wrapper_path = workdir / prepare_wrapper_filename

        logger.debug('prepare wrapper', prepare_wrapper_path, level=3)

        # Execute each script on the guest (with default shell options)
        for script in scripts:
            logger.verbose('script', script, 'green')
            script_with_options = tmt.utils.ShellScript(f'{tmt.utils.SHELL_OPTIONS}; {script}')
            self.write(prepare_wrapper_path, str(script_with_options), 'w')
            if not self.is_dry_run:
                prepare_wrapper_path.chmod(0o755)
            guest.push(
                source=prepare_wrapper_path,
                destination=prepare_wrapper_path,
                options=["-s", "-p", "--chmod=755"])
            command: ShellScript
            if guest.become and not guest.facts.is_superuser:
                command = tmt.utils.ShellScript(f'sudo -E {prepare_wrapper_path}')
            else:
                command = tmt.utils.ShellScript(f'{prepare_wrapper_path}')
            guest.execute(
                command=command,
                cwd=workdir,
                env=environment)
