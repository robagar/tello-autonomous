from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='tello_autonomous',
      version='1.0.0',
      description='Flying the Tello drone autonomously',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/robagar/tello-autonomous',
      project_urls={
      },
      author='Rob Agar',
      author_email='tello_asyncio@fastmail.net',
      license='GPL',
      packages=['tello_autonomous'],     
      python_requires=">=3.9",
      install_requires=[
            "tello_asyncio",
            "pyav"
      ])