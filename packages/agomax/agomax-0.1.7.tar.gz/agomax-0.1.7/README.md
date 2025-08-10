# Agomax v0.1.7

Universal Drone Anomaly Detection Python Package

## Folder Structure

- `agomax/` - Python package with backend logic
- `data/` - Place your data files here (e.g., `base.csv`, `random1.csv`, etc.)
- `models/` - Place trained model files here (`kmeans.pkl`, `lof.pkl`, `svm.pkl`, `dbscan.pkl`, `optics.pkl`)
- `configs/` - Place your rules config here (`rules.yaml`)

## Installation

```bash
pip install agomax
```

## Dashboard Usage

```python
import agomax
agomax.dashboard()  # Launches Streamlit dashboard
```

## API Usage

```python
from agomax.detect import agomax_detect

# Using the included demo data
result = agomax_detect(
    data_source='data/crash.csv',    # Package will auto-resolve this path
    mode='offline',
    rules_path='configs/rules.yaml',  # Package will auto-resolve this path
    model_dir='models/'              # Package will auto-resolve this path
)
print(result)

# Or using your own absolute paths
result = agomax_detect(
    data_source='/path/to/your/data.csv',
    mode='offline',
    rules_path='/path/to/your/rules.yaml',
    model_dir='/path/to/your/models/'
)
print(result)
```

## Data Files
The package includes a demo file `crash.csv` in the `data/` folder for testing and demonstration. You can use this file in the dashboard or with the API to see how anomaly detection works out of the box.

For your own experiments, name your data files as in your prototype: `base.csv`, `random1.csv`, `wind1.csv`, `engine1.csv`, `sensor1.csv`, `crash.csv` and place them in the `data/` folder.

## Package Setup

To make this a pip-installable package, use the following `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name='agomax',
    version='0.1.7',
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
        'plotly'
    ],
    include_package_data=True,
    package_data={
        '': ['data/crash.csv', 'configs/rules.yaml', 'models/*.pkl'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
```

Or use a `pyproject.toml` for modern builds.
