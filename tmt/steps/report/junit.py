import os

import click
from junit_xml import TestCase, TestSuite

import tmt
from tmt.steps.execute import TEST_OUTPUT_FILENAME


def duration_to_seconds(duration):
    """ Convert valid duration string in to seconds """
    h, m, s = duration.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


class ReportJUnit(tmt.steps.report.ReportPlugin):
    """
    Write test results in JUnit format

    When FILE is not specified output is written to the 'junit.xml'
    located in the current workdir.
    """

    # Supported methods
    _methods = [tmt.steps.Method(name='junit', doc=__doc__, order=50)]

    _keys = ['file']

    @classmethod
    def options(cls, how=None):
        """ Prepare command line options for connect """
        return [
            click.option(
                '--file', metavar='FILE',
                help='Path to the file to store junit to'),
            ] + super().options(how)

    def go(self):
        """ Read executed tests and write junit """
        super().go()

        suite = TestSuite(self.step.plan.name)
        for result in self.step.plan.execute.results():
            logs = {}
            for log_path in result.log:
                logs[os.path.basename(
                    log_path)] = self.step.plan.execute.read(log_path)
            case = TestCase(
                result.name,
                classname=None,
                elapsed_sec=duration_to_seconds(result.duration),
                log=logs.get(TEST_OUTPUT_FILENAME, None)
                )
            if result.result == 'error':
                case.add_error_info("error")
            elif result.result == "fail":
                case.add_failure_info("fail")
            suite.test_cases.append(case)
        f_path = self.opt("file", self.workdir + '/junit.xml')
        with open(f_path, 'w') as fw:
            TestSuite.to_file(fw, [suite])
        self.info("junit", f_path, 'green')
