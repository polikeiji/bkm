import setuptools

with open("README.md", "r") as fh:
    long_desctiption = fh.read()

setuptools.setup(
    name='bkm',
    version='0.1.0',
    author='Keiji Hokamura',
    author_email='polikeiji@gmail.com',
    description='Simple hierarchical CLI bookmark manager',
    long_desctiption=long_desctiption,
    long_desctiption_content_type='text/markdown',
    url='https://github.com/polikeiji/bkm',
    packages==setuptools.find_packages(),
    py_modules=['bkm'],
    install_requires=[
        'PyYAML',
        'click',
    ],
    entry_points='''
        [console_scripts]
        bkm=bkm:bkm
    ''',
)
