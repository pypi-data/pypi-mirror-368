from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name='djstruct-savane',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description="Générateur automatique de structure templates/static pour projet Django",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SAVANE Mouhamed',
    author_email='savanemouhamed05@gmail.com',
    entry_points={
        'console_scripts': [
            'gn-djstruct = template_static.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
    ],
    python_requires='>=3.6',
    install_requires=[],
)
