from setuptools import setup, find_packages


setup(
        name='krystal',
        version='0.0.0',
        description="Krystal's static website builder",
        author='krystalgamer',
        author_email='krystalgamer@protonmail.com',
        url='https://github.com/krystalgamer/krystal',
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'krystal = krystal.main:main'
                ]

            }
)
