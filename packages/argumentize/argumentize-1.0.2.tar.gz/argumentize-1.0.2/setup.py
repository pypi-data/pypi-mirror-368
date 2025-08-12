from setuptools import setup


def readme():
    with open('ReadMe.md') as f:
        return f.read()


setup(
    name='argumentize',
    version='1.0.2',
    packages=['argumentize'],
    url='',
    license='MIT License',
    author='liubomyr.ivanitskyi',
    author_email='lubomyr.ivanitskiy@gmail.com',
    description='Simple library for patching function inner scope ',
    long_description=readme(),
    long_description_content_type="text/markdown"
)