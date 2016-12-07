from setuptools import setup, find_packages

setup(
    name='phscrap',
    version='0.1',
    author='Juan Schandin',
    author_email='jschandin@gmail.com',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points="""
    [console_scripts]
    phscrap = scrap.phscrap:main
    """
)
