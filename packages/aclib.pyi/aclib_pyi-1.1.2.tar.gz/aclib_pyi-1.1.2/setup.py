from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aclib.pyi',
    version='1.1.2',
    author='AnsChaser',
    author_email='anschaser@163.com',
    description='compile and pack python project to exe with pyd.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AnsChaser/aclib.pyi',
    python_requires='>=3.6',
    install_requires=['Cython', 'pyinstaller'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ]
)
