from setuptools import setup

setup(
    name='phscrap',
    version='0.1',
    author='Juan Schandin',
    author_email='jschandin@gmail.com',
    py_modules=['phscrap'],
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points="""
    [console_scripts]
    phscrap = phscrap:main
    """
)
