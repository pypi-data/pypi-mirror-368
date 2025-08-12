from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class CustomInstallCommand(install):
    def run(self):
        # Install dependencies from requirements.txt
        os.system('pip install -r requirements.txt')
        # Run the default install process
        install.run(self)
setup(
    name='Neutrophils Maturation Classifier',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,  # This ensures non-Python files are included
    package_data={
        '': [
            'assets/icon.png',
            # 'assets/icon.ico'
            ],  # Include the icon file in the package
    },
    entry_points={
        'console_scripts': [
            'neu-classifier = app:main',
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
    }
)