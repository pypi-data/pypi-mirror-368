# flake8: noqa: E501
from markdown_to_slack_mkdown import slack_convert, SlackConvertOptions


class TestSlackConvert:
    def test_basic(self):
        assert slack_convert("a") == "a"
        assert slack_convert("text **bold** more-text") == "text *bold* more-text"
        assert slack_convert("text ~~strike~~ more-text") == "text ~strike~ more-text"
        # Mix of strike + bold
        assert slack_convert("text ~~strike~~ more**bold**-te**x**t") == "text ~strike~ more*bold*-te*x*t"

    def test_links(self):
        assert (
            slack_convert("text [This is link title](http://www.foo.com) more-text")
            == "text <http://www.foo.com|This is link title> more-text"
        )
        assert (
            slack_convert("[text] [This is link title](http://www.foo.com) more-text")
            == "[text] <http://www.foo.com|This is link title> more-text"
        )
        # Two links and bold
        assert (
            slack_convert("text [Google](http://google.com/) ([x**BB**x](https://xxx.com/)) more-text")
            == "text <http://google.com/|Google> (<https://xxx.com/|x*BB*x>) more-text"
        )

    def test_lists(self):
        list_github = """   *
    aaa
				* *
    bbb  * cccc
*
    ddd
      *"""
        list_slack = """   •
    aaa
				• *
    bbb  * cccc
•
    ddd
      •"""
        assert slack_convert(list_github) == list_slack

        list_github = """* test1
* test2"""
        list_slack = """• test1
• test2"""
        assert slack_convert(list_github) == list_slack


class TestSlackHeadlinesOption:
    def test_release_message(self):
        msg_github = """# [1.50.0](https://github.com/foo/boo/compare/v1.49.3...v1.50.0) (2015-02-12)
### Features
 * add GET /v1/events ([#134](https://github.com/foo/boo/issues/134)) ([1726806](https://github.com/foo/boo/commit/1726806))
 * remove DELETE /v1/message ([#121](https://github.com/foo/boo/issues/121)) ([3523r42](https://github.com/foo/boo/commit/3523r42))"""

        msg_slack = """# <https://github.com/foo/boo/compare/v1.49.3...v1.50.0|1.50.0> (2015-02-12)
### Features
 • add GET /v1/events (<https://github.com/foo/boo/issues/134|#134>) (<https://github.com/foo/boo/commit/1726806|1726806>)
 • remove DELETE /v1/message (<https://github.com/foo/boo/issues/121|#121>) (<https://github.com/foo/boo/commit/3523r42|3523r42>)"""

        assert slack_convert(msg_github) == msg_slack

    def test_headlines_parse(self):
        opt_with_headlines = SlackConvertOptions(headlines=True)
        assert slack_convert("### fooo", opt_with_headlines) == "*fooo*"
        assert slack_convert(" # Boo foo 123", opt_with_headlines) == "*Boo foo 123*"
        assert slack_convert("\n\t### Features\n", opt_with_headlines) == "\n*Features*\n"
        assert slack_convert("## Features\r\n\r\nA feature", opt_with_headlines) == "*Features*\n\nA feature"

        msg_github = """# [1.50.0](https://github.com/foo/boo/compare/v1.49.3...v1.50.0) (2015-02-12)
### Features
 * add GET /v1/events ([#134](https://github.com/foo/boo/issues/134)) ([1726806](https://github.com/foo/boo/commit/1726806))
 * remove DELETE /v1/message ([#121](https://github.com/foo/boo/issues/121)) ([3523r42](https://github.com/foo/boo/commit/3523r42))"""

        msg_slack_headlines_bold = """*<https://github.com/foo/boo/compare/v1.49.3...v1.50.0|1.50.0> (2015-02-12)*
*Features*
 • add GET /v1/events (<https://github.com/foo/boo/issues/134|#134>) (<https://github.com/foo/boo/commit/1726806|1726806>)
 • remove DELETE /v1/message (<https://github.com/foo/boo/issues/121|#121>) (<https://github.com/foo/boo/commit/3523r42|3523r42>)"""

        assert slack_convert(msg_github, opt_with_headlines) == msg_slack_headlines_bold


class TestSlackRepoNameOption:
    def test_issue_references(self):
        assert (
            slack_convert(
                "Enhance link regexp #134",
                SlackConvertOptions(repo_name="eritikass/githubmarkdownconvertergo"),
            )
            == "Enhance link regexp <https://github.com/eritikass/githubmarkdownconvertergo/pull/134|#134>"
        )

        actual_input = """
	• add GET /v1/events (#134)
	• remove DELETE /v1/message, (#121)
	• remove DELETE /v1/message (#121)
	• fix UPDATE /v1/user/meta, #123"""

        expected = """
	• add GET /v1/events (<https://github.com/foo-owner/boo-repo/pull/134|#134>)
	• remove DELETE /v1/message, (<https://github.com/foo-owner/boo-repo/pull/121|#121>)
	• remove DELETE /v1/message (<https://github.com/foo-owner/boo-repo/pull/121|#121>)
	• fix UPDATE /v1/user/meta, <https://github.com/foo-owner/boo-repo/pull/123|#123>"""

        assert slack_convert(actual_input, SlackConvertOptions(repo_name="foo-owner/boo-repo")) == expected

        assert (
            slack_convert(
                "multiple refs, #55, #56",
                SlackConvertOptions(repo_name="eritikass/githubmarkdownconvertergo"),
            )
            == "multiple refs, <https://github.com/eritikass/githubmarkdownconvertergo/pull/55|#55>, <https://github.com/eritikass/githubmarkdownconvertergo/pull/56|#56>"
        )

        assert (
            slack_convert(
                "multiple refs, #55; #56",
                SlackConvertOptions(repo_name="eritikass/githubmarkdownconvertergo"),
            )
            == "multiple refs, <https://github.com/eritikass/githubmarkdownconvertergo/pull/55|#55>; <https://github.com/eritikass/githubmarkdownconvertergo/pull/56|#56>"
        )

        assert (
            slack_convert(
                "multiple refs, #55, #56, #22225 ... and radom text",
                SlackConvertOptions(repo_name="eritikass/githubmarkdownconvertergo"),
            )
            == "multiple refs, <https://github.com/eritikass/githubmarkdownconvertergo/pull/55|#55>, <https://github.com/eritikass/githubmarkdownconvertergo/pull/56|#56>, <https://github.com/eritikass/githubmarkdownconvertergo/pull/22225|#22225> ... and radom text"
        )


class TestSlackGithubUsername:
    def test_usernames(self):
        assert slack_convert("@eritikass") == "<https://github.com/eritikass|@eritikass>"
        assert slack_convert("@roman-shandurenko") == "<https://github.com/roman-shandurenko|@roman-shandurenko>"
        assert slack_convert("@someone2Awesome8") == "<https://github.com/someone2Awesome8|@someone2Awesome8>"
        assert slack_convert("@soXeo-ne2Awes-ome8") == "<https://github.com/soXeo-ne2Awes-ome8|@soXeo-ne2Awes-ome8>"
        assert slack_convert("example@example.com") == "example@example.com"
        assert slack_convert("foo @eritikass booo!") == "foo <https://github.com/eritikass|@eritikass> booo!"


class TestSlackCustomRefPatterns:
    def test_custom_patterns(self):
        assert (
            slack_convert(
                "JIRA-35",
                SlackConvertOptions(
                    custom_ref_patterns={
                        r"(?P<BOARD>JIRA|DEVOPS)-(?P<ID>\d+)": "https://xxx.atlassian.net/browse/${BOARD}-${ID}"
                    }
                ),
            )
            == "https://xxx.atlassian.net/browse/JIRA-35"
        )

        assert (
            slack_convert(
                " JIRA-1   ",
                SlackConvertOptions(
                    custom_ref_patterns={r"JIRA-(?P<ID>\d+)": "https://xxx.atlassian.net/browse/JIRA-${ID}"}
                ),
            )
            == " https://xxx.atlassian.net/browse/JIRA-1   "
        )

        assert (
            slack_convert(
                " [JIRA-1]   ",
                SlackConvertOptions(
                    custom_ref_patterns={r"JIRA-(?P<ID>\d+)": "https://xxx.atlassian.net/browse/JIRA-${ID}"}
                ),
            )
            == " [https://xxx.atlassian.net/browse/JIRA-1]   "
        )

        assert (
            slack_convert(
                " (JIRA-1)   ",
                SlackConvertOptions(
                    custom_ref_patterns={r"JIRA-(?P<ID>\d+)": "https://xxx.atlassian.net/browse/JIRA-${ID}"}
                ),
            )
            == " (https://xxx.atlassian.net/browse/JIRA-1)   "
        )

        assert (
            slack_convert(
                " (JIRA-1, UPS-23)   ",
                SlackConvertOptions(
                    custom_ref_patterns={
                        r"(?P<BOARD>JIRA|UPS)-(?P<ID>\d+)": "https://xxx.atlassian.net/browse/JIRA-${ID}"
                    }
                ),
            )
            == " (https://xxx.atlassian.net/browse/JIRA-1, https://xxx.atlassian.net/browse/JIRA-23)   "
        )

        assert (
            slack_convert(
                "JIRA-356",
                SlackConvertOptions(
                    custom_ref_patterns={
                        r"(?P<BOARD>JIRA|DEVOPS)-(?P<ID>\d{1,10})": "https://xxx.atlassian.net/browse/${BOARD}-${ID}"
                    }
                ),
            )
            == "https://xxx.atlassian.net/browse/JIRA-356"
        )

        assert (
            slack_convert(
                "XXX JIRA-12 UUU",
                SlackConvertOptions(
                    custom_ref_patterns={r"JIRA-(?P<ID>\d+)": "https://xxx.atlassian.net/browse/JIRA-${ID}"}
                ),
            )
            == "XXX https://xxx.atlassian.net/browse/JIRA-12 UUU"
        )

        assert (
            slack_convert(
                "XXXJIRA-2YYY",
                SlackConvertOptions(
                    custom_ref_patterns={r"JIRA-(?P<ID>\d+)": "https://xxx.atlassian.net/browse/JIRA-${ID}"}
                ),
            )
            == "XXXJIRA-2YYY"
        )

        input_long = """
	- JIRA-666: foo-booo (leg-123)
	- eventum-1335: cat was here (LEGAL-19)
	- ticket:555: lorem ipsum something-something"""

        expected_long = """
	- <https://xxx.atlassian.net/browse/JIRA-666|JIRA-666>: foo-booo (leg-123)
	- <https://eventum.example.com/issue.php?id=1335|eventum-1335>: cat was here (<https://xxx.atlassian.net/browse/LEGAL-19|LEGAL-19>)
	- <https://example.com/t/555|ticket-555>: lorem ipsum something-something"""

        assert (
            slack_convert(
                input_long,
                SlackConvertOptions(
                    custom_ref_patterns={
                        r"(?P<BOARD>JIRA|DEVOPS|LEGAL|COPY|PASTA)-(?P<ID>\d+)": "[${BOARD}-${ID}](https://xxx.atlassian.net/browse/${BOARD}-${ID})",
                        r"eventum-(?P<ID>\d+)": "[eventum-${ID}](https://eventum.example.com/issue.php?id=${ID})",
                        r"ticket:(?P<ID>\d+)": "<https://example.com/t/${ID}|ticket-${ID}>",
                    }
                ),
            )
            == expected_long
        )

        assert (
            slack_convert(
                input_long,
                SlackConvertOptions(
                    custom_ref_patterns={
                        r"(?P<BOARD>[A-Z]{3,10})-(?P<ID>\d{2,5})": "[${BOARD}-${ID}](https://xxx.atlassian.net/browse/${BOARD}-${ID})",
                        r"eventum-(?P<ID>\d+)": "[eventum-${ID}](https://eventum.example.com/issue.php?id=${ID})",
                        r"ticket:(?P<ID>\d+)": "<https://example.com/t/${ID}|ticket-${ID}>",
                    }
                ),
            )
            == expected_long
        )

        assert (
            slack_convert(
                "example_com",
                SlackConvertOptions(custom_ref_patterns={r"example_com": "https://example.com"}),
            )
            == "https://example.com"
        )
