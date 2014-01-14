import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="GithubCommitMailer",
      version="0.1.0",
      author="Raghu Rajagopalan",
      author_email="raghu.nospam@gmail.com",
      description=("Get colorized diffs from github pushes"),
      license = "BSD",
      keywords = "github, git",
      url = "https://bitbucket.org/raghur/GithubCommitMailer",
      packages=['githubmailer'],
      install_requires = [
          'pypandoc',
          'google-api-python-client',
          'python-gflags',
          'httplib2'
      ],
      entry_points = {
          'console_scripts': [
    'easyblogger = blogger.blogger:main'
                         ]
                     },
      long_description='see https://bitbucket.org/raghur/GithubCommitMailer',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
          ],
)
