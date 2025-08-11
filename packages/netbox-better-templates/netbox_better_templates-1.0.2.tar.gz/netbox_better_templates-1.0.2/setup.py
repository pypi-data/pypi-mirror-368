from setuptools import find_packages, setup

setup(
    name='netbox-better-templates',
    version='1.0.2',
    description='Adds some functionality to netbox templates and config render.',
    author='Radin System',
    author_email='technical@rsto.ir',
    url='https://github.com/radin-system/netbox-better-templates',
    install_requires=[],
    packages=find_packages(
        include = [
            'netbox_better_templates',
            'netbox_better_templates.*',
        ],
    ),
    include_package_data=True,
    zip_safe=False,
)