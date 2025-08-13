# 📖 Guide

## 1️⃣ Install

1. install `brew`: https://brew.sh/

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. install `pipx`

```
brew install pipx
pipx ensurepath
```

3. install `v-cr`

```
pipx install v-magic-code-review
```

## 2️⃣ Setup environment variables

```
# jira
export JIRA_HOST=https://jira.********.com
export JIRA_TOKEN=OTY**************************Y4

# confluence
export CONFLUENCE_HOST=https://wiki.********.com
export CONFLUENCE_TOKEN=MDQ2**************************1u

# gitlab
export GITLAB_HOST=https://gitlab.********.com
export GITLAB_TOKEN=_PH*****************UiW

# gemini
export GEMINI_COOKIE_SECURE_1PSID=g.a0KAaMS************************************************AROiSJgW0076
export GEMINI_COOKIE_SECURE_1PSIDTS=sidts-CjAB*****************************KZn7ScYuMQAA
```

### 如何获取上述 Variables ？

| Variable                       | How to Get                                                                                       |
|--------------------------------|--------------------------------------------------------------------------------------------------|
| `JIRA_TOKEN`                   | Go to Jira → 右上角头像点击 Profile → Personal Access Tokens → Create token                             |
| `CONFLUENCE_TOKEN`             | Go to Confluence → 右上角头像点击 Settings → Personal Access Tokens → Create token                      |
| `GITLAB_TOKEN`                 | Go to GitLab → 左上角头像点击 Preferences → Access Tokens → Add new token                               |
| `GEMINI_COOKIE_SECURE_1PSID`   | Login to Gemini → F12 打开 Developer Tools → Application → Cookies → Copy value：`__Secure-1PSID`   |
| `GEMINI_COOKIE_SECURE_1PSIDTS` | Login to Gemini → F12 打开 Developer Tools → Application → Cookies → Copy value：`__Secure-1PSIDTS` |

## 3️⃣ Usage

```
$ v-cr -h
usage: cli.py [-h] [-m MR_ID] [-o] [-c] [--prompt-template PROMPT_TEMPLATE] [--list-prompt-template] [--debug] [--version] [JIRA_KEY]

Magic Code Review

positional arguments:
  JIRA_KEY              jira issue key

options:
  -h, --help            show this help message and exit
  -m MR_ID, --mr-id MR_ID
                        merge request id
  -o, --only-code       only review code diff
  -c, --copy-prompt     copy prompt to clipboard
  --prompt-template PROMPT_TEMPLATE
                        specific prompt template
  --list-prompt-template
                        list all prompt templates
  --debug
  --version
```

### 自动发送给 Gemini

```
$ v-cr ORI-100000
```

### 手动发送给 Gemini

```
$ v-cr ORI-100000 -c
......
......
2025-06-12 11:13:32,126 - INFO - ✨ issue comments length: 420
2025-06-12 11:13:33,231 - INFO - ✨ code  diff length: 990
2025-06-12 11:13:33,387 - INFO - ✨ prompt length: 28737, tokens num: 13015
✅ Prompt 已复制到剪贴板
```

### 自定义 Prompt

#### 创建

```
$ cd ~/.local/share/v-cr/prompts
```

```
$ touch my-prompt.txt
```

#### 变量说明

| 变量                     | 说明                         |
|------------------------|----------------------------|
| `{issue_summary}`      | Jira Issue 标题              |
| `{issue_requirements}` | Jira Issue Description     |
| `{issue_design}`       | Jira Issue 关联的设计 Wiki      |
| `{issue_comments}`     | Jira Issue 的评论             |
| `{mr_description}`     | Gitlab Merge Request 的描述   |
| `{mr_diff}`            | Gitlab Merge Request 的代码变更 |

#### Prompt 示例

```
帮我优化一下代码变量命名

{mr_diff}
```

```
帮我看下需求和实现的代码是否一致，是否漏了需求

<section>需求</section>
{issue_requirements}

<section>代码实现 Diff</section>
{mr_diff}
```

#### 列出可用的 Prompts

```
$ v-cr --list-prompt-template
Avalible Prompt Templates:

 • DEFAULT
 • my-prompt
```

#### 指定 Prompt

```
$ v-cr ORI-100000 --prompt-template my-prompt
```

# 🤝 Contributing

1. install `poetry`

```
brew install poetry
```

2. install virtualenv and dependencies

```
poetry install --with dev
```
