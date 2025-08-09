---
title: README
author: Jan-Michael Rye
---

[insert: badges gitlab]: #

[![License](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/MIT.html) [![Pipeline Status](https://gitlab.inria.fr/jrye/prometa/badges/main/pipeline.svg)](https://gitlab.inria.fr/jrye/prometa/-/commits/main) [![PyPI](https://img.shields.io/badge/PyPI-Prometa-006dad.svg)](https://pypi.org/project/Prometa/) [![PyPI Downloads](https://static.pepy.tech/badge/Prometa)](https://pepy.tech/projects/Prometa) [![Hatch](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![Latest Release](https://gitlab.inria.fr/jrye/prometa/-/badges/release.svg)](https://gitlab.inria.fr/jrye/prometa/-/tags) [![isort](https://img.shields.io/badge/imports-isort-1674b1.svg?labelColor=ef8336)](https://pypi.org/project/isort/) [![Black](https://img.shields.io/badge/code_style-black-000000.svg)](https://pypi.org/project/black/) [![Pylint](https://gitlab.inria.fr/jrye/prometa/-/jobs/artifacts/main/raw/pylint/pylint.svg?job=pylint)](https://gitlab.inria.fr/jrye/prometa/-/jobs/artifacts/main/raw/pylint/pylint.txt?job=pylint)

[/insert: badges gitlab]: #

# Synopsis

Prometa is a tool to help automate the management of project metadata, such as updating codemeta.json files and inserting command output and other examples into the README. It was originally a collection of utility scripts that were written to handle a growing number of projects. These scripts were then generalized and consolidated to create Prometa.

Prometa does not directly modify existing local files. Instead, it will create a temporary file with the suggested changes and then launch a user-configurable file merger ([vimdiff](https://www.vim.org/) by default) for the user to interactively select which modifications to integrate.

## Functionality

Prometa is under active development. New functionality is currently driven by the author's own needs but suggestions (via email or issue) and merge requests to add new functionality are welcome. The rest of this section gives an overview what is currently implemented.

### General

* Centralize common data such as author names, email addresses, affiliations and [ORCID](https://orcid.org/) and [HAL](https://hal.science/) identifiers in custom configuration files to ensure that they remain up-to-date across multiple projects (see [Configuration File Example](#configuration-file-example)).
* Automatically insert data into README files (see [README Content Insertion](#readme-content-insertion)).
* Generate common metadata files:
    - [codemeta.json](https://codemeta.github.io/user-guide/): Generated with [CodeMetaPy](https://pypi.org/project/CodeMetaPy/) from pyproject.toml and other supported files. Prometa handles bugs with the current version of CodeMetaPy that prevent it from processing README and license objects.
    - [CITATION.cff](https://citation-file-format.github.io/): Generated from the Prometa configuration file and the generated codemeta.json file.
* Discover remote identifiers and link to corresponding pages on common third-party software trackers:
    - [Software Heritage](https://www.softwareheritage.org/)
    - [HAL (open archive)](https://hal.science/)

### GitLab

* Generate GitLab CI configurations (see [GitLab CI Job Management](#gitlab-ci-job-management)).
* Manage various GitLab badges (see [GitLab Badge Management](#gitlab-badge-management)).
* Create GitLab hooks (see [GitLab Hook Management](#gitlab-hook-management)
* Configure project description from local metadata.
* Set merge method.
* Configure protected branches.
* Configure protected tags.

### Python

* Update [pyproject.toml](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/):
    - Update author data from central Prometa configuration file.
    - Update project URLs based on current Git remote origin.
    - Update classifiers based on detected SPDX license type. 
* Manage Python-specific badges on GitLab (e.g. Pylint score, Black, isort).


## Links

[insert: links 2]: #

### GitLab

* [Homepage](https://gitlab.inria.fr/jrye/prometa)
* [Source](https://gitlab.inria.fr/jrye/prometa.git)
* [Issues](https://gitlab.inria.fr/jrye/prometa/issues)
* [Documentation](https://jrye.gitlabpages.inria.fr/prometa)
* [GitLab package registry](https://gitlab.inria.fr/jrye/prometa/-/packages)

### Other Repositories

* [Python Package Index (PyPI)](https://pypi.org/project/Prometa/)
* [Software Heritage](https://archive.softwareheritage.org/browse/origin/?origin_url=https%3A//gitlab.inria.fr/jrye/prometa.git)

[/insert: links 2]: #


# Installation

## From Source

~~~
git clone https://gitlab.inria.fr/jrye/prometa.git
pip install -U prometa
~~~

## From GitLab Package Registry

Follow the instructions in the link provided above.


# Usage

Prometa provides the `prometa` command-line utility to update project metadata. It should be invoked with the directory paths of the target projects. See the next section about configuration and `prometa --help` for details.

[insert: command_output prometa -h]: #

~~~
usage: prometa [-h] [--config PATH [PATH ...]] [--gen-config PATH]
               [--list-config {all,existing}] [--no-xdg] [--trust]
               [path ...]

Update project metadata.

positional arguments:
  path                  Path to project directory.

options:
  -h, --help            show this help message and exit
  --config PATH [PATH ...]
                        By default, prometa will search for configuration
                        files named "prometa.yaml" or ".prometa.yaml" in the
                        target directory and all of its parent directories,
                        with precedence given to configuration files closest
                        to the target directory. Additional configuration file
                        paths can be passed with this option and they will
                        take precedence over the detected configuration files.
                        If multiple configuration paths are given with this
                        command, their order determines their precedence.
  --gen-config PATH     Generate a configuration file template at the given
                        path. If the path is "-", the file will be printed to
                        STDOUT. Note that prometa will only look for files
                        named "prometa.yaml" or ".prometa.yaml".
  --list-config {all,existing}
                        List either all paths that will be scanned for
                        configuration files for each given project, or only
                        existing ones. The output is printed as a YAML file
                        mapping project directory paths to lists of possible
                        configuration files.
  --no-xdg              Disable loading of configuration files in standard XDG
                        locations.
  --trust               It is possible to insert arbitrary command output into
                        the README file. By default, prometa will prompt the
                        user for confirmation before running the command to
                        prevent arbitrary code execution in the context of a
                        collaborative environment. This option can be used to
                        disable the prompt if the user trusts all of the
                        commands in the README.

~~~

[/insert: command_output prometa -h]: #


# Configuration

Prometa loads configuration files named `prometa.yaml` or `.prometa.yaml` in the current project directory and any parent thereof. These files will be merged internally to create a single configuration, with files in child directories taking precedence over their parent. This allows the user to keep common settings in a parent directory while allowing more specific settings in the context of a specific project or group of projects. Configuration files may also be placed in standard [XDG configuration directory locations](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html). These will be loaded with the lowest priority.


## Configuration File Example

Please see the following commented configuration file for examples of supported fields.

[insert: command_output:yaml prometa --gen-config -]: #

~~~yaml
# A list of authors. They will appear in various files (e.g. pyproject.toml,
# codemeta.json, CITATIONS.cff).
authors:
    # Given names (required)
  - given-names: John

    # Family names (required)
    family-names: Doe

    # Email (optional)
    email: john.doe@example.com

    # Affiliation (optional)
    affiliation: Example Institute

    # ORCID identifier (optional)
    orcid: XXXX-XXXX-XXXX-XXXX

    # HAL Open Science identifier (optional)
    hal: XXXXXXX

# If true, create missing CITATIONS.cff files.
citations_cff: true

# GitLab settings (optional)
gitlab:
  # Prometa uses python-gitlab to manage GitLab hooks that push code to other
  # open repositories (currently only Software Heritage). python-gitlab requires
  # both a configuration file and the name of the section in the configuration
  # file to use for a given project. For details, see the documentation:
  #
  # https://python-gitlab.readthedocs.io/en/stable/cli-usage.html#cli-configuration
  #
  # python-gitlab configuration file:
  config: path/to/python-gitlab.cfg

  # The section of the python-gitlab configuration file to use when retrieving
  # GitLab project data.
  section: somewhere

  # If true, update the project description.
  update_description: true

  # Set the merge policy (merge, rebase_merge, ff).
  merge_method: ff

  # Configure protect branches. The key is the branch name and the value is
  # either a dict or null. Null values will unprotect the corresponding branch.
  # Dict values contain the following keys to configure how the branch is
  # protected:
  #
  #   merge: who is allowed to merge
  #   push: who is allowed to push and merge
  #   push_force: a boolean indicating if force push is allowed
  #
  # merge and push_and_merge accept either an integer access level or any of the
  # constants defined in gitlab.confg.AccessLevel:
  # https://python-gitlab.readthedocs.io/en/stable/api/gitlab.html#gitlab.const.AccessLevel
  protected_branches:
      main:
          merge: maintainers
          push: maintainers
          push_force: false

  # Configure protected tags. The key is the tag string and the value is the
  # access level or null. Null values will unproctect the tag. Access level
  # values are the same as those for protected branches.
  projected_tags:
      "v*": maintainers

  # Some CI jobs such as updating GitLab pages and registering packages should
  # only be done on specific main branches. These can be configured here.
  main_branches:
      - main

  # If true, update project hooks.
  update_hooks: false

  # Configure various badges for GitLab projects. Enabled badges will be
  # created, updated and deleted according to specific conditions. For example,
  # PyPI downloads will only be created if a pyproject.toml file exists and the
  # corresponding project exists on PyPI.
  #
  # Please consult the badges documentation in the README or examing the code in
  # prometa.git.gitlab.badges for more information on supported badges. Please
  # feel free to suggest new badges by opening an issue or by emailing the
  # maintainer directly.
  #
  # Example:
  enabled_badges:
      - Pipeline Status
      - License
      - PyPI
      - PyPI Downloads
      - Hatch

  # Configure which CI jobs are managed.
  enabled_ci_jobs:
      - pages
      - register_python_package
      - release_job

  # Configure which hooks are enabled.
  enabled_hooks:
      - Software Heritage

  # Map GitLab hosts to their corresponding GitLab Pages URL formats. This map
  # will be used to generate documentation links when a "pages" job is detected
  # in the CI configuration file. The namespace and name parameters correspond
  # to those of the GitLab project.
  pages_urls:
    gitlab.com: "https://{namespace}.gitlab.io/{name}"

  # The regular expression for matching release tags. If given, a CI release job
  # will be created for tags that match this pattern. Omit this or set it to
  # null to disable release jobs.
  release_tag_regex: "^v."

  # Configure tags for GitLab CI jobs. This is a mapping of Python regular
  # expressions to lists of tags. Jobs that match the regular expressions will
  # be tagged with the corresponding tags. If multiple regular expressions match
  # a job then it will accumulate the tags.
  #
  # To apply the same tags to all jobs, use the regular expression ".".
  ci_tags:
      ".":
        - tag1
        - tag2
        - tag3

# By default, Prometa will attempt to detect each project's license using the
# spdx-matcher Python package. In some cases the detection fails (e.g. GPL v2
# and GPL v2-only use the same license text). This option can be set to an SPDX
# license identifier (https://spdx.org/licenses/) to force a particular license
# when the detection fails. If null or an empty strign then it will be ignored.
#
# Note that it will not download a new license file or modify the existing
# license file.
license: null

# The utility to use when merging changes. It must accept two file paths (the
# modified file and the original) and return non-zero exit status to indicate an
# error or abort.
merger: vimdiff


# The README interpolator can insert command output into the README. To prevent
# arbitrary command execution, Prometa will prompt the user to confirm a command
# before it is executed. This prompt can be surpressed for trusted READMEs by
# setting the following to true.
trust_commands: false

~~~

[/insert: command_output:yaml prometa --gen-config -]: #

# README Content Insertion

Content can be inserted into the README.md file using invisible comments of the format:

[insert: verbatim]: #

~~~markdown

[insert: <label>]: #

...

[/insert: <label>]: #
~~~

[/insert: verbatim]: #


Both the opening and closing tags must be preceded by empty lines to remain invisible when the Markdown is converted to other formats.

The label will determine which content is inserted and everything between the opening and closing insert comments will be replaced with the content specified by the label. The labels may be indented, in which case the inserted content will also be indented to the same level.

Prometa currently recognizes the following labels.

[insert: command_output:embedded_markdown prometa-document_labels 2]: #

## badges

~~~
[insert: badges <api> [<api> ...]]: #

<content>

[/insert: badges <api> [<api> ...]]: #
~~~

Insert all badges currently configured on the project's Git host.
`<api>` specifies the API to use to query the badges. Currently only
the following value is supported.

gitlab
: Insert all badges from the project's remote GitLab instance
origin.  The badges are retrieved via calls to the GitLab API so
this requires the "gitlab" section to be configured in the project's
configuration file (see the configuration section for details).


## citations

~~~
[insert: citations <level>]: #

<content>

[/insert: citations <level>]: #
~~~

Convert CITATIONS.cff to different formats using with
[cffconvert](https://pypi.org/project/cffconvert/) and insert them
into the README.

The `<level>` parameter is an integer to indicate the heading level
of the current context. It will be used to insert nested headers in
the content. If omitted, level 1 is assumed.


## command_output[

~~~
[insert: command_output[:<lang>] <command string>]: #

<content>

[/insert: command_output[:<lang>] <command string>]: #
~~~

Insert the output of an arbitrary command. The user will be prompted
to confirm the command before it is run to prevent unknowingly
executing arbitrary code, unless Prometa is currently configured to
trust all commands (e.g. via the `--trust` command-line option).

`<command string>` should be a valid shell command string. It will
be interpreted internally using
[shlex.split()](https://docs.python.org/3/library/shlex.html#shlex.split).
The confirmation prompt will show the user the parsed command.

The output will be wrapped in a code block. The user may specify an
optional language for syntax highlighting by appending `:<lang>` to
the end of the `command_output` label, where `<lang>` is the desired
language. For example, to insert YAML output, use
`command_output:yaml command arg1 arg2 ...`.

The command also supports the custom language tag
"embedded_markdown", which will insert the command's output into the
Markdown document directly instead of fencing it in a code block.


## links

~~~
[insert: links <level>]: #

<content>

[/insert: links <level>]: #
~~~

Insert project links such as homepage, source code repository, issue
tracker, documentation, etc. Optional third-part repository links
(PyPI, SWH, HAL) will also be inserted if Prometa detects that they
contain the project.

The `<level>` parameter is an integer to indicate the heading level
of the current context. It will be used to insert nested headers in
the content. If omitted, level 1 is assumed.


## verbatim

~~~
[insert: verbatim]: #

<content>

[/insert: verbatim]: #
~~~

Return the content between the invisible comments as-is. This no-op
label can be used to wrap examples of other labels and anything else
that should not be modified.

[/insert: command_output:embedded_markdown prometa-document_labels 2]: #


# GitLab Badge Management

Various badges can be managed automatically via the GitLab API. Each badge must
be first enabled in the configuration file's `gitlab.enabled_badges` list. Once
enabled in that list, the specific conditions for each badge will be checked. If
the badges condition's are met, the badge will be created or updated as
necessary. If the condition is not met then the badge will be deleted if it
exists.

For example, the "PyPI" badge will check if the project includes a
`pyproject.toml` file and if that name in that file corresponds to a project on
[PiPI](https://pypi.org/). If it does, a PyPI badge will be created with a link
to the project on PyPI. If the project does not exist on PyPI (or there is no
`pyproject.toml` file), than any existing badge named "PyPI" will be removed.

This will only occur if "PyPI" is in the last of enabled badged in the
configuration file. Badges not in that list are not managed.

The following table shows the currently supported badges. To manage a badge with
Prometa, include its name in the list of enabled badges in the configuration
file.

[insert: command_output:embedded_markdown prometa-document_gitlab_badges]: #

|Name|Description|Condition|
|:- |:- |:- |
|Black|The Python package uses [Black](https://pypi.org/project/black/) for code formatting.|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project includes a Python package.<br />AND<br />Black is included in a list named `enabled_badges` in the `[tool.prometa]` section of the project's pyproject.toml file, e.g. `enabled_badges = ["Black"]`.|
|Hatch|The Python package uses the [Hatch](https://hatch.pypa.io/latest/) build system.|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project includes a Python package.<br />AND<br />The package is configured to use Hatch via pyproject.toml.|
|Latest Release|The latest tagged release on the project's GitLab host. This uses the built-in GitLab release badge.|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project's GitLab CI file contains a release job.|
|License|The project's license name, as recognized by [SPDX](https://spdx.org/licenses/).|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project has a recognized SPDX license.|
|Pipeline Status|The current pipeline status on the project's GitLab host. This uses the built-in GitLab pipeline badge.|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The GitLab CI configuration file exists.|
|PyPI|The Python project's name on [PyPI](https://pypi.org/).|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project includes a Python package.<br />AND<br />The package exists on PyPI.|
|PyPI Downloads|Estimated number of downloads from [PyPI](https://pypi.org/).|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project includes a Python package.<br />AND<br />The package exists on PyPI.|
|Pylint|Display the [Pylint](https://pylint.readthedocs.io/en/stable/) score.|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project includes a Python package.|
|Test Coverage|Display the currently configured [test coverage](https://docs.gitlab.com/ci/testing/code_coverage/) results.|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project's GitLab CI file contains test jobs with coverage fields.|
|isort|The Python package sorts imports with [isort](https://pypi.org/project/isort/).|The badge's name is in the `gitlab.enabled_badges` list in the configuration file.<br />AND<br />The project includes a Python package.<br />AND<br />isort is included in a list named `enabled_badges` in the `[tool.prometa]` section of the project's pyproject.toml file, e.g. `enabled_badges = ["isort"]`.|

[/insert: command_output:embedded_markdown prometa-document_gitlab_badges]: #


# GitLab CI Job Management

Various jobs in the GitLab CI configuration file can be managed, such as creating a release job whenever a release tag is pushed. The job management is enabled by adding the corresponding job name to the `gitlab.enabled_ci_jobs` array in the configuration file.

[insert: command_output:embedded_markdown prometa-document_gitlab_ci_jobs]: #

|Name|Description|Condition|
|:- |:- |:- |
|pages|This does not create the pages job. It only updates it to set the following fields: "artifacts", "only" and "stage".|The job's name is in the `gitlab.enabled_ci_jobs` list in the configuration file.|
|pylint|Add a job to get a Pylint score and save a badge with the score as an artifact.|The job's name is in the `gitlab.enabled_ci_jobs` list in the configuration file.<br />OR<br />The corresponding Pylint badge is enabled.|
|register_python_package|Add a job to build and register a Python package if the project contains one, or remove the job it is exists but the project does not contain a Python package.|The job's name is in the `gitlab.enabled_ci_jobs` list in the configuration file.|
|release_job|Add a release job that triggers when Git release tags are pushed. The release tag regular expression can be set in the configuration file.|The job's name is in the `gitlab.enabled_ci_jobs` list in the configuration file.|

[/insert: command_output:embedded_markdown prometa-document_gitlab_ci_jobs]: #


# GitLab Hook Management

Currently only the Software Heritage hook is managed but others may be added later.

[insert: command_output:embedded_markdown prometa-document_gitlab_hooks]: #

|Name|Description|Condition|
|:- |:- |:- |
|Software Heritage|Hook to prompt [Software Heritage](https://www.softwareheritage.org/) to archive the project when it is updated.|The hook's name is in the `gitlab.enabled_hooks` list in the configuration file.|

[/insert: command_output:embedded_markdown prometa-document_gitlab_hooks]: #

