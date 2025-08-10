from blueness.pypi import setup

from bluer_journal import NAME, VERSION, DESCRIPTION, REPO_NAME

setup(
    filename=__file__,
    repo_name=REPO_NAME,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    packages=[
        NAME,
        f"{NAME}.classes",
        f"{NAME}.help",
        f"{NAME}.tests",
        f"{NAME}.utils",
        f"{NAME}.utils.sync",
    ],
    include_package_data=True,
    package_data={
        NAME: [
            "config.env",
            "sample.env",
            ".abcli/**/*.sh",
        ],
    },
)
