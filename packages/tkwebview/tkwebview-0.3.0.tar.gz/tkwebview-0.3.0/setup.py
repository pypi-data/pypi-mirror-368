from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(name='tkwebview',
      version='0.3.0',
      description='tkinter的webview视图',
      author='Smart-Space',
      author_email='smart-space@qq.com',
      url='https://github.com/Smart-Space/tkwebview',
      packages=find_packages(),
      long_description=long_description,
      long_description_content_type="text/markdown",
      license="MIT",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent"],
      include_package_data = True,
      python_requires='>=3.7',  # Python的版本约束(from webviewpy)
      install_requires=[],
      )
