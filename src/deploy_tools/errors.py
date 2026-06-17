class DeployToolsError(Exception):
    """Base class for expected, user-facing deploy-tools errors.

    These represent actionable failure conditions, such as invalid configuration or a
    corrupt deployment area, where the exception message is itself the guidance the
    operator needs. The CLI catches this base class at the top level and prints the
    message without a traceback (see ``deploy_tools.__main__.main``). Any exception that
    is *not* a ``DeployToolsError`` is treated as an unexpected bug and surfaces with a
    full traceback.
    """
