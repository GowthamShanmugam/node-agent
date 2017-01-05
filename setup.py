import re
from setuptools import find_packages
from setuptools import setup


def extract_requirements(filename):
    with open(filename, 'r') as requirements_file:
        return [
            x[:-1] for x in requirements_file.readlines()
            if not x.startswith("#") and x[:-1] != ''
        ]

install_requires = extract_requirements('requirements.txt')


def read_module_contents():
    with open('tendrl/node_agent/__init__.py') as app_init:
        return app_init.read()

module_file = read_module_contents()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
version = metadata['version']


setup(
    name="tendrl-node-agent",
    version=version,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
                                    "tests"]),
    namespace_packages=['tendrl'],
    url="http://www.redhat.com",
    author="Rohan Kanade.",
    author_email="rkanade@redhat.com",
    license="LGPL-2.1+",
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'tendrl-node-agent = tendrl.node_agent.manager.manager:main'
        ]
    }
)
