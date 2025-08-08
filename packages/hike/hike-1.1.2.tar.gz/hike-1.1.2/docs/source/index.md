# Introduction

```{.textual path="docs/screenshots/basic_app.py" title="Hike" lines=40 columns=120 press="tab,d,ctrl+t"}
```

Hike is a [Markdown](https://commonmark.org/help/) browser for the terminal.
It provides the ability to browse for and view local Markdown files, as well
as Markdown files that can be downloaded from the web. It also has shortcuts
that make it easy to view Markdown files on popular
[git](https://git-scm.com/doc)
[forges](https://en.wikipedia.org/wiki/Forge_(software)) such as
[GitHub](https://github.com/), [GitLab](https://about.gitlab.com),
[Codeberg](https://codeberg.org) and [Bitbucket](https://bitbucket.org).

## Installation

### pipx

The application can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
pipx install hike
```

### Homebrew

The package is available via [Homebrew](https://brew.sh). Use the following
commands to install:

```sh
brew tap davep/homebrew
brew install hike
```

### Other installation methods

The following installation methods have been provided by third parties.

!!! warning

    Please note that I don't maintain any of these installation
    methods and so can't vouch for them myself. I can't guarantee that they
    are up-to-date, neither can I guarantee that they install the original code.

    **Use them at your own risk**.

#### X-CMD

The application can be installed using [`x-cmd`](https://x-cmd.com):

```sh
x install hike
```

## Running Hike

Once you've installed Hike using one of the [above methods](#installation),
you can run the application using the `hike` command.

### Command line options

Hike has a number of command line options; they include:

#### `-b`, `--bindings`

Prints the application commands whose keyboard bindings can be modified,
giving the defaults too.

```sh
hike --bindings
```
```bash exec="on" result="text"
hike --bindings
```

#### `-h`, `--help`

Prints the help for the `hike` command.

```sh
hike --help
```
```bash exec="on" result="text"
hike --help
```

#### `--license`, `--licence`

Prints a summary of Hike's license.

```sh
hike --license
```
```bash exec="on" result="text"
hike --license
```

#### `--navigation`

Starts Hike with the navigation panel visible; this overrides and modifies
the saved state of the navigation panel.

#### `--no-navigation`

Starts Hike with the navigation panel hidden; this overrides and modifies
the saved state of the navigation panel.

#### `-t`, `--theme`

Sets Hike's theme; this overrides and changes any previous theme choice made
[via the user interface](configuration.md#theme).

To see a list of available themes use `?` as the theme name:

```sh
hike --theme=?
```
```bash exec="on" result="text"
hike --theme=?
```

#### `-v`, `--version`

Prints the version number of Hike.

```sh
hike --version
```
```bash exec="on" result="text"
hike --version
```

#### The startup command

Hike can also take a command on the command line, which will be processed
via its own [internal command line](commands.md). This means that you have
access to the full array of Hike features. This means you can do something
as simple as give the name of a file to view:

```sh
hike view-this.md
```

or you can [view a README file hosted on a forge](commands.md#viewing-files-on-forges):

```sh
hike gh davep/org-davep-2bit
```

## Getting help

A great way to get to know Hike is to read the help screen. Once in the
application you can see this by pressing <kbd>F1</kbd>.

```{.textual path="docs/screenshots/basic_app.py" title="The Hike Help Screen" press="f1" lines=50 columns=120}
```

The help will adapt to which part of the screen has focus, providing extra
detail where appropriate; so while the example shown above shows the help
related to [Hike's command line](commands.md), here's the help when the
markdown document has focus:

```{.textual path="docs/screenshots/basic_app.py" title="Markdown Document Help" press="tab,f1" lines=50 columns=120}
```

### The command palette

Another way of discovering commands and keys in Hike is to use the command
palette (by default you can call it with <kbd>ctrl</kbd>+<kbd>p</kbd> or
<kbd>meta</kbd>+<kbd>x</kbd>).

```{.textual path="docs/screenshots/basic_app.py" title="The Hike Command Palette" press="ctrl+p" lines=50 columns=120}
```

## Questions and feedback

If you have any questions about Hike, or you have ideas for how it might be
improved, do please feel free to [visit the discussion
area](https://github.com/davep/hike/discussions) and [ask your
question](https://github.com/davep/hike/discussions/categories/q-a) or
[suggest an
improvement](https://github.com/davep/hike/discussions/categories/ideas).

When doing so, please do search past discussions and also [issues current
and previous](https://github.com/davep/hike/issues) to make sure I've not
already dealt with this, or don't have your proposed change already flagged
as something to do.

[//]: # (index.md ends here)
