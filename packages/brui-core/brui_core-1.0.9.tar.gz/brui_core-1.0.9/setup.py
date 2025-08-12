from setuptools import setup, find_packages

setup(
    name='brui_core',
    version='1.0.9',
    packages=find_packages(),
    install_requires=[
        'playwright==1.42.0',
        'pyperclip',
    ],
    extras_require={
        'test': [
            'pytest-playwright==0.4.4',
            'playwright==1.42.0',
            'pytest-asyncio',
        ],
    },
    author='Ryan Zheng',
    author_email='ryan.zheng.work@gmail.com',
    description='Core browser UI automation framework',
    long_description='''
    A flexible and robust browser UI automation framework that provides:
    - Browser management and launching
    - Configuration handling
    - Clipboard management
    - Base UI integration capabilities
    
    To install with testing dependencies:
    pip install brui_core[test]
    ''',
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/AutoByteus/brui_core.git',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
    python_requires='>=3.8',
)
