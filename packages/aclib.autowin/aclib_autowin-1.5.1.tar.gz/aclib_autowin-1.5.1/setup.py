from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aclib.autowin',
    version='1.5.1',
    author='AnsChaser',
    author_email='anschaser@163.com',
    description='auto window task',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AnsChaser/aclib.autowin',
    python_requires='>=3.6',
    install_requires=['aclib.builtins', 'aclib.winlib'],
    extras_require={
        'cv': ['aclib.cv'],
        'dm': ['aclib.dm'],
        'full': ['aclib.autowin[cv,dm]'],
        'dev': ['aclib.autowin[full]', 'aclib.pip', 'build', 'twine']
    },
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
