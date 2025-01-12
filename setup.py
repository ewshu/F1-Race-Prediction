from setuptools import setup, find_packages

setup(
    name='f1-race-winner-prediction',  # Use a concise, unique name for your project
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'flask-cors',
    ],
    entry_points={
        'console_scripts': [
            'f1-predictor=src.models.app:main',  # Adjust as needed
        ],
    },
    # Additional metadata
    author='Eshwar',
    author_email='pamula.3@osu.edu',
    description='A web application for predicting F1 race winners.',
    url='https://github.com/ewshu/F1-Race-Winner-Prediction',
)
