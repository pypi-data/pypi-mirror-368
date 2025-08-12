import re
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SlackConvertOptions:
    """Options to fine-tune GitHub to Slack markdown convert"""

    headlines: bool = False
    repo_name: Optional[str] = None
    github_url: str = "https://github.com"
    custom_ref_patterns: Dict[str, str] = field(default_factory=dict)


def slack_convert(markdown: str, options: Optional[SlackConvertOptions] = None) -> str:
    """Convert GitHub markdown to Slack markdown format

    Args:
        markdown: GitHub markdown text to convert
        options: Optional conversion options

    Returns:
        Slack-formatted markdown text
    """
    if options is None:
        options = SlackConvertOptions()

    github_url = options.github_url or "https://github.com"

    # Using start and end patterns to ensure we don't match in the middle of words
    start_of_pattern = r"(?P<THE_START_OF_MATCH>^|[\s\[\(])"
    end_of_pattern = r"(?P<THE_END_OF_MATCH>$|[\s:\]\),.!])"

    # Apply custom reference patterns
    if options.custom_ref_patterns:
        for pattern, replacement in options.custom_ref_patterns.items():
            try:
                regex = re.compile(f"{start_of_pattern}{pattern}{end_of_pattern}")
                # Convert ${NAME} to \g<NAME> for Python regex
                python_replacement = replacement
                import re as re_module

                for match in re_module.finditer(r"\$\{([^}]+)\}", replacement):
                    group_name = match.group(1)
                    python_replacement = python_replacement.replace(f"${{{group_name}}}", f"\\g<{group_name}>")
                markdown = regex.sub(rf"\g<THE_START_OF_MATCH>{python_replacement}\g<THE_END_OF_MATCH>", markdown)
            except re.error as e:
                print(f"ERROR_USING_CustomRefPatterns: {e}")
                continue

    # Convert usernames @xxx
    username_regex = re.compile(start_of_pattern + r"@(?P<USERNAME>[a-z-A-Z0-9]{3,20})" + end_of_pattern)
    markdown = username_regex.sub(
        rf"\g<THE_START_OF_MATCH><{github_url}/\g<USERNAME>|@\g<USERNAME>>\g<THE_END_OF_MATCH>",
        markdown,
    )

    # Normalize newlines
    markdown = markdown.replace("\r\n", "\n")

    # Convert bold **TEXT** -> *TEXT* (must be done before list markers)
    bold_regex = re.compile(r"(?s)(\*\*).+?(\*\*)")

    def replace_bold(match: re.Match[str]) -> str:
        return match.group(0).replace("**", "*")

    markdown = bold_regex.sub(replace_bold, markdown)

    # Convert strikethrough ~~TEXT~~ -> ~TEXT~
    strike_regex = re.compile(r"(?s)(~~).+?(~~)")

    def replace_strike(match: re.Match[str]) -> str:
        return match.group(0).replace("~~", "~")

    markdown = strike_regex.sub(replace_strike, markdown)

    # Convert links [TEXT](link) -> <link|TEXT>
    link_regex = re.compile(r"(?s)\[(?P<name>[^\]]+)\]\((?P<link>[^)]+)\)")

    def replace_link(match: re.Match[str]) -> str:
        name = match.group("name")
        link = match.group("link")
        if name and link:
            return f"<{link}|{name}>"
        return match.group(0)

    markdown = link_regex.sub(replace_link, markdown)

    # Convert list markers * -> • (must be done after bold conversion)
    # Only match * that is followed by whitespace or is at end of line
    list_regex = re.compile(r"^(\s*)\*(?=\s|$)", re.MULTILINE)
    markdown = list_regex.sub(r"\1•", markdown)

    # Convert headlines to bold if option is set
    if options.headlines:
        headline_regex = re.compile(r"^(\t?[ ]{0,15}#{1,4}[ ]{1,})(.+)", re.MULTILINE)
        markdown = headline_regex.sub(r"*\2*", markdown)

    # Convert issue/PR references #<number> to links
    if options.repo_name:
        issue_regex = re.compile(r"([\s(,;])([#])(\d{1,10})([):\s]|,|;|$)")

        def replace_issue(match: re.Match[str]) -> str:
            return f"{match.group(1)}<{github_url}/{options.repo_name}/pull/{match.group(3)}|{match.group(2)}{match.group(3)}>{match.group(4)}"  # noqa: E501

        markdown = issue_regex.sub(replace_issue, markdown)

    return markdown
