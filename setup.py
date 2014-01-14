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
      url = "https://github.com/raghur/github_commit_mailer",
      packages=['githubmailer'],
      install_requires = [
          'jinja2',
          'pygments'
      ],
      entry_points = {
          'console_scripts': [
    'github_mailer = githubmailer.githubmailer:main'
                         ]
                     },
      long_description='see https://github.com/raghur/github_commit_mailer',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
          ],
)
