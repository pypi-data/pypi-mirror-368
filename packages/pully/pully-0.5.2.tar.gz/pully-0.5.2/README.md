# pully

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/sandbox/pully?branch=main)](https://gitlab.com/saferatday0/sandbox/pully/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/sandbox/pully?branch=main)](https://gitlab.com/saferatday0/sandbox/pully/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/sandbox/pully)](https://gitlab.com/saferatday0/sandbox/pully/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![cici enabled](https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33)](https://gitlab.com/saferatday0/cici)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

`pully` is a tool for managing a large number of Git repository checkouts
effectively.

## Why `pully`

`pully` was created to make managing and automating changes to multiple projects
easier. There are two general use cases `pully` is designed to address. First, a
mass action where a a set of projects is cloned and the same action is run on
each project. Second, managing a local workspace for a set of projects.

### Large scale changes

`pully` helps solve problems where you need to make the same
action across multiple projects.

- Update the copyright date in the license file of all projects.
- Update pre-commit versions in all projects.
- Add [`badgie`](https://gitlab.com/saferatday0/badgie) to all projects.

The recommended workflow in this case is to use `pully` to clone workspaces for
mass actions not regular development. Avoid using the same project workspaces
for both regular development and automated actions. Different branches, new
files, and unknown state that are common in work in progress are likely to
interfere with scripted changes.

### Manage local workspaces

`pully` can be used to do an initial clone of projects for regular development.
This is convenient when onboarding new developers or setting up a new
environment. Common tasks like pulling the latest main or pruning remote
branches are easy to do. Beware of scripting changes to multiple projects since
the status of each project may different and cause unexpected results.

We recommend only automating commands that update the local workspace not any
that push changes to prevent accidents. We expect to automate some common update
tasks in the future.

## Installation

```sh
python3 -m pip install pully
```

## Usage

### Initialize a project workspace

Run `pully init` to create a project workspace.

```sh
pully init
```

A `.pully.json` will be created in the current directory that will be used to
track project checkouts.

### Add a project for tracking

Only newly added projects will be printed.

Track a group by path:

```sh
pully add -G saferatday0
```

Track a subgroup by path:

```sh
pully add -G saferatday0/infra
```

Track a project by path:

```sh
pully add -P saferatday0/badgie
```

### Pull local copy

Call `pully` with no options to clone or pull the project to your local filesystem:

```sh
pully
```

This is the same as calling `pully pull`:

```sh
pully pull
```

### Advanced usage

`pully` allows you to customize your local checkout for different use cases.

Check out an arbitary subset of projects:

```sh
pully add -P saferatday0/badgie
pully add -P saferatday0/cici
pully add -G saferatday0/library
pully
```
