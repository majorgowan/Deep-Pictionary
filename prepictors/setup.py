from setuptools import setup

setup(name='prepictors',
        version='0.1',
        description='Predictors for Deep Pictionary app',
        url='http://github.com/majorgowan/pictionary',
        author='Mark Fruman',
        author_email='majorgowan@yahoo.com',
        license='MIT',
        packages=['knn'],
        install_requires=['numpy'],
        zip_safe=False)
