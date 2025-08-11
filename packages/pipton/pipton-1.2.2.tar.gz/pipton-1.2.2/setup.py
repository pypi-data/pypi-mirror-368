from setuptools import setup, find_packages

setup(
    name='pipton',
    version='1.2.2',  # نسخه جدید
    packages=find_packages(),  # جایگزین py_modules
    include_package_data=True,
    
    entry_points={
        'console_scripts': [
            'pipton = pipton.pipton_repl:start_repl',
            'pipton-run = pipton.run_pipton:main',
        ],
    },

    install_requires=[],
    
    author='AmirhosseinPython',
    author_email='amirhossinpython03@gmail.com',
    description='A custom language with Persian-flavored syntax and full Python power',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/amirhossinpython/pipton_lang',
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Intended Audience :: Developers",
        "Natural Language :: Persian",
    ],
    
    python_requires='>=3.6',
)