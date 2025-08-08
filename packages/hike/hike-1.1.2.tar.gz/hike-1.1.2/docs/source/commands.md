# Introduction

Central to Hike's user interface is a command line; similar to a shell's
command line. It has a history (use the <kbd>up</kbd> and <kbd>down</kbd>
keys to navigate) as well as history auto-completion (use <kbd>right</kbd>
to accept a suggestion).

!!! tip

    Full help for all of the commands is [available inside Hike itself](index.md#getting-help) by
    pressing <kbd>F1</kbd> while the command line has focus.

## The commands

### Opening a file

There are three different ways to open a file for viewing, from the command
line; they are:

#### With a file name

To open a local file, type in the name (including the path to it if it's not
in the current working directory).

```{.textual path="docs/screenshots/basic_app.py" title="Entering a file's location" lines=25 columns=80 press="~,/,m,y,a,p,p,/,R,E,A,D,M,E,.,m,d"}
```

#### With a URL

To open a file that is hosted on a website, type in the URL:

```{.textual path="docs/screenshots/basic_app.py" title="Entering a URL to view" lines=25 columns=80 press="h,t,t,p,s,:,/,/,r,a,w,.,g,i,t,h,u,b,u,s,e,r,c,o,n,t,e,n,t,.,c,o,m,/,d,a,v,e,p,/,2,b,i,t,.,e,l,/,r,e,f,s,/,h,e,a,d,s,/,m,a,i,n,/,R,E,A,D,M,E,.,m,d"}
```

#### Via a file opening dialog

To open a file opening dialog at a specific directory, type in the directory
you want to start browsing at:

```{.textual path="docs/screenshots/basic_app.py" title="Entering a directory to browse" lines=25 columns=80 press="~,/,d,e,v,e,l,o,p,/,p,y,t,h,o,n,/,h,i,k,e,/,d,o,c,s,/,s,o,u,r,c,e"}
```

and after you get <kbd>Enter</kbd> the dialog will open:

```{.textual path="docs/screenshots/basic_app.py" title="Browsing for a file to open" lines=40 columns=120 press="~,/,d,e,v,e,l,o,p,/,p,y,t,h,o,n,/,h,i,k,e,/,d,o,c,s,/,s,o,u,r,c,e,enter"}
```

### Navigation panel

There are some commands that interact with the navigation panel. These are:

#### `bookmarks`

!!! aliases

    `b` `bm`

Ensures that the navigation panel is opened and then jumps to the bookmarks.

#### `contents`

!!! aliases

    `c` `toc`

Ensures that the navigation panel is opened and then jumps to the Markdown
document's table of contents.

#### `history`

!!! aliases

    `h`

Ensures that the navigation panel is opened and then jumps to the document
history.

#### `local`

!!! aliases

    `l`

Ensures that the navigation panel is opened and then jumps to the local file
system browser.

### Viewing files on forges

Hike supports quickly viewing Markdown documents hosted on popular forges, the available commands are:

#### Forge commands

##### `bitbucket`

!!! alias

    `bb`

Loads and views a file hosted on [Bitbucket](https://bitbucket.org/).

##### `codeberg`

!!! alias

    `cb`

Loads and views a file hosted on [Codeberg](https://codeberg.org/).

##### `github`

!!! alias

    `gh`

Loads and views a file hosted on [GitHub](https://github.com/).

##### `gitlab`

!!! alias

    `gl`

Loads and views a file hosted on [GitLab](https://gitlab.com/).

#### Specifying the file to view

When using the forge commands listed above, a number of methods of
specifying the file to view are supported:

| Format                           | Effect                                                      |
|----------------------------------|-------------------------------------------------------------|
| `<owner>/<repo>`                 | Open `README.md` from a repository                          |
| `<owner> <repo>`                 | Open `README.md` from a repository                          |
| `<owner>/<repo> <file>`          | Open a specific file from a repository                      |
| `<owner> <repo> <file>`          | Open a specific file from a repository                      |
| `<owner>/<repo>:<branch>`        | Open `README.md` from a specific branch of a repository     |
| `<owner> <repo>:<branch>`        | Open `README.md` from a specific branch of a repository     |
| `<owner>/<repo>:<branch> <file>` | Open a specific file from a specific branch of a repository |
| `<owner> <repo>:<branch> <file>` | Open a specific file from a specific branch of a repository |

So, for example, if you want to view Hike's README:

```
gh davep/hike
```

Or if you want to view Hike's change-log:

```
gh davep/hike ChangeLog.md
```

If you wanted to view the README file but in a feature branch called `revamp-readme`:

```
gh davep/hike:revamp-readme
```

etc.

### Other commands

Other useful commands include:

#### `chdir <dir>`

!!! aliases

    `cd`, `dir`, `ls`

Where `<dir>` is the path to a directory. This will change the root
directory of the tree in the local file system browser in the navigation
panel.

#### `changelog`

!!! aliases

    `cl`

Loads and views Hike's [ChangeLog](changelog.md).

#### `help`

!!! aliases

    `?`

Shows Hike's help dialog.

#### `obsidian`

!!! aliases

    `obs`

Changes the root directory of the tree in the local file system browser in
the navigation panel so that it points to the root directory of your
Obsidian vaults (obviously only useful if you are an
[Obsidian](https://obsidian.md/) user).

#### `readme`

Loads and views Hike's README.

[//]: # (commands.md ends here)
