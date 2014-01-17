from unittest import TestCase
from mock import Mock
from githubmailer import GithubDiffColorizer


class GithubColorizerTests(TestCase):

    def setUp(self):
        self.token = "abcd"
        self.colorizer = GithubDiffColorizer(self.token)

    def tearDown(self):
        pass

    def test_should_colorize_diffs(self):
        """@todo: Docstring for should_colorize_diffs.

        :arg1: @todo
        :returns: @todo

        """
        self.colorizer.get_diff_for_commit = Mock(return_value="___diff___")
        diff = self.colorizer.colorize_diffs("owner", "repo", "sha")

        self.colorizer \
            .get_diff_for_commit.called_with("owner", "repo", "sha")
        self.assertTrue("___diff___" in diff)
