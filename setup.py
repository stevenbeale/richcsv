import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='csvcurse',  
     version='0.1',
     scripts=['csvcurse'] ,
     author='Steven Beale',
     author_email='steven.t.beale@gmail.com',
     description='A terminal application for browsing csv data',
     long_description=long_description,
     long_description_content_type="text/markdown",
     url='https://github.com/stevenbeale/csvcurse',
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
