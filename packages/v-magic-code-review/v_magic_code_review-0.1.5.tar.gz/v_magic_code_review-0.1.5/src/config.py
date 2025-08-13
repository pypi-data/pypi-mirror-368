import os


class GitlabConfig:
    PROJECT_ID = 311
    HOST = os.environ['GITLAB_HOST']
    TOKEN = os.environ['GITLAB_TOKEN']
    DIFF_EXCLUDE_EXT = {'.ttf', '.woff', '.woff2', '.eot', '.otf', '.svg', '.png', '.jpg', '.jpeg', '.gif'}
    DIFF_EXCLUDE_PATH = {'thirdparty'}


class JiraConfig:
    HOST = os.environ['JIRA_HOST']
    TOKEN = os.environ['JIRA_TOKEN']


class JiraField:
    SUMMARY = 'summary'
    AC = 'customfield_13530'
    DESCRIPTION = 'description'
    COMMENT = 'comment'


class ConfluenceConfig:
    HOST = os.environ['CONFLUENCE_HOST']
    TOKEN = os.environ['CONFLUENCE_TOKEN']


class GeminiConfig:
    COOKIE_SECURE_1PSID = os.environ['GEMINI_COOKIE_SECURE_1PSID']
    COOKIE_SECURE_1PSIDTS = os.environ['GEMINI_COOKIE_SECURE_1PSIDTS']
