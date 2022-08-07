from setuptools import setup, find_packages


setup(
        name='krystal',
        version='1.0.3',
        description="Krystal's static website builder",
        author='krystalgamer',
        author_email='krystalgamer@protonmail.com',
        url='https://github.com/krystalgamer/krystal',
        packages=find_packages(),
		install_requires=[
			'Flask>=2.0.3',
			'Frozen-Flask>=0.18',
			'marko>=1.2.0',
			'Pygments>=2.11.2'
		],
        entry_points={
            'console_scripts': [
                'krystal = krystal.main:main'
                ]

            }
)
