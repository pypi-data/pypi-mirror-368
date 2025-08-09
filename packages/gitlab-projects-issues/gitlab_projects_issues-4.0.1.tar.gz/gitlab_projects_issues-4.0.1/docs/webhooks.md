---
hide:
  - toc
---

# gitlab-projects-issues

<!-- markdownlint-disable no-inline-html -->

[![Release](https://img.shields.io/pypi/v/gitlab-projects-issues?color=blue)](https://pypi.org/project/gitlab-projects-issues)
[![Python](https://img.shields.io/pypi/pyversions/gitlab-projects-issues?color=blue)](https://pypi.org/project/gitlab-projects-issues)
[![Downloads](https://img.shields.io/pypi/dm/gitlab-projects-issues?color=blue)](https://pypi.org/project/gitlab-projects-issues)
[![License](https://img.shields.io/gitlab/license/RadianDevCore/tools/gitlab-projects-issues?color=blue)](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/-/blob/main/LICENSE)
<br />
[![Build](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/badges/main/pipeline.svg)](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/-/commits/main/)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gitlab-projects-issues&metric=bugs)](https://sonarcloud.io/dashboard?id=RadianDevCore_gitlab-projects-issues)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gitlab-projects-issues&metric=code_smells)](https://sonarcloud.io/dashboard?id=RadianDevCore_gitlab-projects-issues)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gitlab-projects-issues&metric=coverage)](https://sonarcloud.io/dashboard?id=RadianDevCore_gitlab-projects-issues)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gitlab-projects-issues&metric=ncloc)](https://sonarcloud.io/dashboard?id=RadianDevCore_gitlab-projects-issues)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gitlab-projects-issues&metric=alert_status)](https://sonarcloud.io/dashboard?id=RadianDevCore_gitlab-projects-issues)
<br />
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](https://commitizen-tools.github.io/commitizen/)
[![gcil](https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/gcil)
[![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)

Generate GitLab project issues and milestones statistics automatically

---

[TOC]

<span class="page-break"></span>

## Issues access token

- **Settings:**
    - **Action:** Add new token
    - **Token name:** `<path/to/webhooks/project>-reporter-api`
    - **Expiration date:** `yyyy-12-31`
    - **Select a role:** `Reporter`
    - **Select scopes:**
        - **api:** Enable
    - **Action:** Create project access token
    - **Your new project access token:**
        - **Action:** Copy project access token

---

<span class="page-break"></span>

## CI/CD webhooks project

- **Settings / CI/CD / Variables:**
    - **Action:** Add variable
        - **Visibility:** Masked and hidden
        - **Protect variable:** Enable
        - **Expand variable reference:** Enable
        - **Key:** `GITLAB_TOKEN`
        - **Value:** `PASTE_<path/to/webhooks/project>-reporter-api_TOKEN`
        - **Action:** Add variable

- **Settings / Access tokens:**
    - **Action:** Add new token
        - **Token name:** `webhook-issues`
        - **Expiration date:** `yyyy-12-31`
        - **Select a role:** `Maintainer`
        - **Select scopes:**
            - **api:** Enable
        - **Action:** Create project access token
    - **Your new project access token:**
        - **Action:** Copy project access token

- **Repository sources with a `gitlab-projects-issues` CI/CD pipeline:**

```yaml title="Webhooks / README.md"
--8<-- "webhooks/README.md"
```

```yaml title="Webhooks / .gitignore"
--8<-- "webhooks/.gitignore"
```

<span class="page-break"></span>

```yaml title="Webhooks / .gitlab-ci.yml"
--8<-- "webhooks/.gitlab-ci.yml"
```

---

<span class="page-break"></span>

## Issues webhook configuration

- **Settings / Webhooks:**
    - **Action:** Add new webhook
        - **URL:** `https://<GITLAB_DOMAIN>/api/v4/projects/<PATH%2FTO%2FWEBHOOK%2FPROJECT>/pipeline?ref=<BRANCH>`
        - **Action:** Add custom headers
            - **Header name:** `PRIVATE-TOKEN`
            - **Header value:** `PASTE_webhook-issues_TOKEN`
        - **Name:** `gitlab-projects-issues`
        - **Trigger:**
            - **Issues events:** Enable
        - **Enable SSL verification:** Enable
        - **Action:** Add webhook
    - **Action:** Test (`gitlab-projects-issues`) / Issue events
