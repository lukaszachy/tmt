# coding: utf-8

""" Common options and the MethodCommand class """

import re
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type

import click

import tmt.lint
import tmt.log
import tmt.utils

# When dealing with older Click packages (I'm looking at you, Python 3.6),
# we need to define FC on our own.
try:
    from click.decorators import FC

except ImportError:
    from typing import TypeVar, Union

    FC = TypeVar('FC', bound=Union[Callable[..., Any], click.Command])  # type: ignore[misc]


if TYPE_CHECKING:
    import tmt.cli


MethodDictType = Dict[str, click.core.Command]

# Originating in click.decorators, an opaque type describing "decorator" functions
# produced by click.option() calls: not options, but decorators, functions that attach
# options to a given command.
# Since click.decorators does not have a dedicated type for this purpose, we need
# to construct it on our own, but we can re-use a typevar click.decorators has.
_ClickOptionDecoratorType = Callable[[FC], FC]
# The type above is a generic type, `FC` being a typevar, so we have two options:
# * each place using the type would need to fill the variable, i.e. add [foo]`, or
# * we could do that right here, because right now, we don't care too much about
# what this `foo` type actually is - what's important is the identity, return type
# matches the type of the argument.
ClickOptionDecoratorType = _ClickOptionDecoratorType[Any]

# Verbose, debug and quiet output
VERBOSITY_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option(
        '-v', '--verbose', count=True, default=0,
        help='Show more details. Use multiple times to raise verbosity.'),
    click.option(
        '-d', '--debug', count=True, default=0,
        help='Provide debugging information. Repeat to see more details.'),
    click.option(
        '-q', '--quiet', is_flag=True,
        help='Be quiet. Exit code is just enough for me.'),
    click.option(
        '--log-topic',
        metavar=f'[{"|".join(topic.value for topic in tmt.log.Topic)}]',
        multiple=True,
        type=str,
        help='If specified, --debug and --verbose would emit logs also for these topics.')
    ]

# Force and dry actions
DRY_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option(
        '-n', '--dry', is_flag=True,
        help='Run in dry mode. No changes, please.'),
    ]

FORCE_DRY_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option(
        '-f', '--force', is_flag=True,
        help='Overwrite existing files and step data.')
    ] + DRY_OPTIONS


# Fix action
FIX_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option('-F', '--fix', is_flag=True, help='Attempt to fix all discovered issues.')
    ]

WORKDIR_ROOT_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option(
        '--workdir-root', metavar='PATH', default=tmt.utils.WORKDIR_ROOT,
        help=f"Path to root directory containing run workdirs. "
             f"Defaults to '{tmt.utils.WORKDIR_ROOT}'.")
    ]


FILTER_OPTIONS: List[ClickOptionDecoratorType] = [
    click.argument(
        'names', nargs=-1, metavar='[REGEXP|.]'),
    click.option(
        '-f', '--filter', 'filters', metavar='FILTER', multiple=True,
        help="Apply advanced filter (see 'pydoc fmf.filter')."),
    click.option(
        '-c', '--condition', 'conditions', metavar="EXPR", multiple=True,
        help="Use arbitrary Python expression for filtering."),
    click.option(
        '--enabled', is_flag=True,
        help="Show only enabled tests, plans or stories."),
    click.option(
        '--disabled', is_flag=True,
        help="Show only disabled tests, plans or stories."),
    click.option(
        '--link', 'links', metavar="RELATION:TARGET", multiple=True,
        help="Filter by linked objects (regular expressions are "
             "supported for both relation and target)."),
    click.option(
        '-x', '--exclude', 'exclude', metavar='[REGEXP]', multiple=True,
        help="Exclude a regular expression from search result."),
    ]


FILTER_OPTIONS_LONG: List[ClickOptionDecoratorType] = [
    click.argument(
        'names', nargs=-1, metavar='[REGEXP|.]'),
    click.option(
        '--filter', 'filters', metavar='FILTER', multiple=True,
        help="Apply advanced filter (see 'pydoc fmf.filter')."),
    click.option(
        '--condition', 'conditions', metavar="EXPR", multiple=True,
        help="Use arbitrary Python expression for filtering."),
    click.option(
        '--enabled', is_flag=True,
        help="Show only enabled tests, plans or stories."),
    click.option(
        '--disabled', is_flag=True,
        help="Show only disabled tests, plans or stories."),
    click.option(
        '--link', 'links', metavar="RELATION:TARGET", multiple=True,
        help="Filter by linked objects (regular expressions are "
             "supported for both relation and target)."),
    click.option(
        '--exclude', 'exclude', metavar='[REGEXP]', multiple=True,
        help="Exclude a regular expression from search result."),
    ]


STORY_FLAGS_FILTER_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option(
        '--implemented', is_flag=True,
        help='Implemented stories only.'),
    click.option(
        '--unimplemented', is_flag=True,
        help='Unimplemented stories only.'),
    click.option(
        '--verified', is_flag=True,
        help='Stories verified by tests.'),
    click.option(
        '--unverified', is_flag=True,
        help='Stories not verified by tests.'),
    click.option(
        '--documented', is_flag=True,
        help='Documented stories only.'),
    click.option(
        '--undocumented', is_flag=True,
        help='Undocumented stories only.'),
    click.option(
        '--covered', is_flag=True,
        help='Covered stories only.'),
    click.option(
        '--uncovered', is_flag=True,
        help='Uncovered stories only.'),
    ]

FMF_SOURCE_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option(
        '--source', is_flag=True, help="Select by fmf source file names instead of object names."
        )
    ]

REMOTE_PLAN_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option('-s', '--shallow', is_flag=True, help='Do not clone remote plan.')
    ]


_lint_outcomes = [member.value for member in tmt.lint.LinterOutcome.__members__.values()]

LINT_OPTIONS: List[ClickOptionDecoratorType] = [
    click.option(
        '--list-checks',
        is_flag=True,
        help='List all available checks.'),
    click.option(
        '--enable-check',
        'enable_checks',
        metavar='CHECK-ID',
        multiple=True,
        type=str,
        help='Run only checks mentioned by this option.'),
    click.option(
        '--disable-check',
        'disable_checks',
        metavar='CHECK-ID',
        multiple=True,
        type=str,
        help='Do not run checks mentioned by this option.'),
    click.option(
        '--enforce-check',
        'enforce_checks',
        metavar='CHECK-ID',
        multiple=True,
        type=str,
        help='Consider linting as failed if any of the checks is not a pass.'),
    click.option(
        '--failed-only',
        is_flag=True,
        help='Display only tests/plans/stories that fail a check.'),
    click.option(
        '--outcome-only',
        metavar='|'.join(_lint_outcomes),
        multiple=True,
        type=click.Choice(_lint_outcomes),
        help='Display only checks with the given outcome.')
    ]


def create_options_decorator(options: List[ClickOptionDecoratorType]) -> Callable[[FC], FC]:
    def common_decorator(fn: FC) -> FC:
        for option in reversed(options):
            fn = option(fn)

        return fn

    return common_decorator


def show_step_method_hints(
        step_name: str,
        how: str,
        logger: tmt.log.Logger) -> None:
    """
    Show hints about available step methods' installation

    The logger will be used to output the hints to the terminal, hence
    it must be an instance of a subclass of tmt.utils.Common (info method
    must be available).
    """
    if step_name == 'provision':
        if how == 'virtual':
            logger.info(
                'hint', "Install 'tmt-provision-virtual' "
                        "to run tests in a virtual machine.", color='blue')
        if how == 'container':
            logger.info(
                'hint', "Install 'tmt-provision-container' "
                        "to run tests in a container.", color='blue')
        if how == 'minute':
            logger.info(
                'hint', "Install 'tmt-redhat-provision-minute' "
                        "to run tests in 1minutetip OpenStack backend. "
                        "(Available only from the internal COPR repository.)",
                        color='blue')
        logger.info(
            'hint', "Use the 'local' method to execute tests "
                    "directly on your localhost.", color='blue')
        logger.info(
            'hint', "See 'tmt run provision --help' for all "
                    "available provision options.", color='blue')
    elif step_name == 'report':
        if how == 'html':
            logger.info(
                'hint', "Install 'tmt-report-html' to format results "
                        "as a html report.", color='blue')
        if how == 'junit':
            logger.info(
                'hint', "Install 'tmt-report-junit' to write results "
                        "in JUnit format.", color='blue')
        logger.info(
            'hint', "Use the 'display' method to show test results "
                    "on the terminal.", color='blue')
        logger.info(
            'hint', "See 'tmt run report --help' for all "
                    "available report options.", color='blue')


def create_method_class(methods: MethodDictType) -> Type[click.Command]:
    """
    Create special class to handle different options for each method

    Accepts dictionary with method names and corresponding commands:
    For example: {'fmf', <click.core.Command object at 0x7f3fe04fded0>}
    Methods should be already sorted according to their priority.
    """

    def is_likely_subcommand(arg: str, subcommands: List[str]) -> bool:
        """ Return true if arg is the beginning characters of a subcommand """
        return any(subcommand.startswith(arg) for subcommand in subcommands)

    class MethodCommand(click.Command):
        _method: Optional[click.Command] = None

        def _check_method(self, context: 'tmt.cli.Context', args: List[str]) -> None:
            """ Manually parse the --how option """
            how = None
            subcommands = (
                tmt.steps.STEPS + tmt.steps.ACTIONS + ['tests', 'plans'])

            for index, arg in enumerate(args):
                # Handle '--how method' or '-h method'
                if arg in ['--how', '-h']:
                    try:
                        how = args[index + 1]
                    except IndexError:
                        pass
                    break
                # Handle '--how=method'
                elif arg.startswith('--how='):
                    how = re.sub('^--how=', '', arg)
                    break
                # Handle '-hmethod'
                elif arg.startswith('-h'):
                    how = re.sub('^-h ?', '', arg)
                    break
                # Stop search at the first argument looking like a subcommand
                elif is_likely_subcommand(arg, subcommands):
                    break

            # Find method with the first matching prefix
            if how is not None:
                for method in methods:
                    if method.startswith(how):
                        self._method = methods[method]
                        break

            if how and self._method is None:
                # Use run for logging, steps may not be initialized yet
                assert context.obj.run is not None  # narrow type
                assert self.name is not None  # narrow type
                show_step_method_hints(self.name, how, context.obj.run._logger)
                raise tmt.utils.SpecificationError(
                    f"Unsupported {self.name} method '{how}'.")

        def parse_args(  # type: ignore[override]
                self,
                context: 'tmt.cli.Context',
                args: List[str]
                ) -> List[str]:
            self._check_method(context, args)
            if self._method is not None:
                return self._method.parse_args(context, args)
            return super().parse_args(context, args)

        def get_help(self, context: 'tmt.cli.Context') -> str:  # type: ignore[override]
            if self._method is not None:
                return self._method.get_help(context)
            return super().get_help(context)

        def invoke(self, context: 'tmt.cli.Context') -> Any:  # type: ignore[override]
            if self._method:
                return self._method.invoke(context)
            return super().invoke(context)

    return MethodCommand
