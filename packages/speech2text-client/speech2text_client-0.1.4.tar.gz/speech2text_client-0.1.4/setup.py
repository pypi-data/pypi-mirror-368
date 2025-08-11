from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='speech2text_client',
    version='0.1.4',
    author='Dmitry Belov',
    author_email='info@speech2text.ru',
    description='Python SDK for speech2text.ru',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://speech2text.ru/',
    packages=find_packages(),
    install_requires=['requests>=2.25.1'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='speech2text s2t распознание ',
    project_urls={
        'Documentation': 'https://github.com/Speech2TextR/s2t-client-python'
    },
    python_requires='>=3.7'
)
