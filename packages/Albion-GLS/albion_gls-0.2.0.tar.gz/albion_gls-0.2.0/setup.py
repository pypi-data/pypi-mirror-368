from setuptools import setup, find_packages

VERSION = '0.2.0' 
DESCRIPTION = 'Albion_GLS'
LONG_DESCRIPTION = 'Albion Interface'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="Albion_GLS", 
        version=VERSION,
        author="GLS",
        author_email="<software@gls.co.za>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        #packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Engineering",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)