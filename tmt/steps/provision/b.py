import click

import tmt


class ProvisionNAME(tmt.steps.provision.ProvisionPlugin):
    """
    blabla .other
    """

    # Guest instance
    _guest = None

    # Supported methods
    _methods = [tmt.steps.Method(name='name.other', doc=__doc__, order=50)]

    def guest(self):
        """ Return the provisioned guest """
        return None

    @classmethod
    def options(cls, how=None):
        return [
            click.option(
                '--bar', is_flag=True,
                help="Option bar"),
            ] + super().options(how)
