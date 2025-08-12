from pathlib import Path
from setuptools import setup

MAIN_PACKAGE = 'heptapod_paas_runner'

scripts = {  # name to (module in main package, function)
    'heptapod-paas-runner': ('paas_dispatcher', 'main'),
    'heptapod-paas-runner-register': ('paas_register', 'main'),
}

VERSION_FILE = 'VERSION'

with open('install-requirements.txt', 'r') as install_reqf:
    install_req = [req.strip() for req in install_reqf]


setup(
    name='heptapod-paas-runner',
    version=Path(MAIN_PACKAGE, VERSION_FILE).read_text().strip(),
    author='Georges Racinet',
    author_email='georges.racinet@cloudcrane.io',
    url='https://foss.heptapod.net/heptapod/heptapod-paas-runner',
    description="Heptapod Runner: Python utilities and subsystems",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords='hg mercurial git heptapod gitlab',
    license='GPLv3+',
    # do not use find_packages, as it could recurse into the Git and
    # Mercurial repositories
    packages=[MAIN_PACKAGE, MAIN_PACKAGE + '.grpc'],
    package_data={MAIN_PACKAGE: [VERSION_FILE]},
    entry_points=dict(
        console_scripts=[
            '{name}={pkg}.{mod}:{fun}'.format(
                pkg=MAIN_PACKAGE, name=name, mod=mod, fun=fun)
            for name, (mod, fun) in scripts.items()],
    ),
    install_requires=install_req
)
