import click

import tmt


class ProvisionNAME(tmt.steps.provision.ProvisionPlugin):
    """
    blabla
    """

    # Guest instance
    _guest = None

    # Supported methods
    _methods = [tmt.steps.Method(name='name', doc=__doc__, order=50)]

    def guest(self):
        """ Return the provisioned guest """
        return None

    @classmethod
    def options(cls, how=None):
        return [
            click.option(
                '--foo', is_flag=True,
                help="Option foo"),
            ] + super().options(how)
