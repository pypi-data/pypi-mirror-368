from setuptools import setup, find_packages

setup(
    name='agomax',
    version='0.1.6',
    author='shaguntembhurne',
    author_email='your@email.com',
    description='Universal Drone Anomaly Detection Python Package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shaguntembhurne/agomax',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'pyyaml',
        'streamlit',
        'plotly',
        'dronekit'
    ],
    include_package_data=True,
    package_data={
        '': ['../data/*.csv', '../configs/*.yaml', '../models/*.pkl', '../streamlit_app.py'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
