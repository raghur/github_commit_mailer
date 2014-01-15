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
        data = {"repository": {"name": "repo", "owner": {"name": "owner"}},
                "commits": [{"id": "sha1"}]}
        self.colorizer.get_diff_for_commit = Mock(return_value="___diff___")
        self.colorizer.colorize_diffs(data)

        self.colorizer \
            .get_diff_for_commit.called_with("repo", "owner", "sha1")
        self.assertTrue("___diff___" in data["commits"][0]["diff"])
        pass
