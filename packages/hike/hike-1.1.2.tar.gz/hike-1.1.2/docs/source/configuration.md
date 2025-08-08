# Introduction

The way that Hike works can be configured using a configuration file. This
section will describe what can be configured and how.

!!! note

    At the moment some configuration can be done via Hike's UI; other things
    require that you edit the configuration file using your preferred text
    editor. Eventually I aim to make everything that can be configured
    configurable within Hike itself.

The location of the configuration file will depend on how your operating
system and its settings; but by default it is looked for in
[`$XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/latest/),
in a `hike` subdirectory. Mostly this will translate to the file being
called `~/.config/hike/configuration.json`.

## Command line location

By default Hike's command line appears at the bottom of the screen, above
the footer of the application. It can be moved to the top of the screen,
below the application header, with the `Change Command Line Location`
command ([`ChangeCommandLineLocation`](#bindable-commands), bound to
<kbd>Ctrl</kbd>+<kbd>Up</kbd> by default).

```{.textual path="docs/screenshots/basic_app.py" title="Command line on top" lines=40 columns=120 press="tab,d,ctrl+up,tab"}
```

## Keyboard bindings

Hike allows for a degree of configuration of its keyboard bindings;
providing a method for setting up replacement bindings for the commands that
appear in the [command palette](index.md#the-command-palette).

### Bindable commands

The following commands can have their keyboard bindings set:

```bash exec="on"
hike --bindings | sed -e 's/^\([A-Z].*\) - \(.*\)$/- `\1` - *\2*/' -e 's/^    \(Default:\) \(.*\)$/    - *\1* `\2`/'
```

### Changing a binding

If you wish to change the binding for a command, edit the configuration file
and add the binding to the `bindings` value. For example, if you wanted to
change the binding used to create a bookmark, changing it from
<kbd>ctrl</kbd>+<kbd>b</kbd> to <kbd>F6</kbd>, and you also wanted to use
<kbd>Shift</kbd>+<kbd>F6</kbd> to jump to the bookmarks, you would set
`bindings` to this:

```json
"bindings": {
    "BookmarkLocation": "f6",
    "JumpToBookmarks": "shift+f6"
}
```

The designations used for keys is based on the internal system used by
[Textual](https://textual.textualize.io); as such [its caveats about what
works where
apply](https://textual.textualize.io/FAQ/#why-do-some-key-combinations-never-make-it-to-my-app).
The main modifier keys to know are `shift`, `ctrl`, `alt`, `meta`, `super`
and `hyper`; letter keys are their own letters; shifted letter keys are
their upper-case versions; function keys are simply <kbd>f1</kbd>,
<kbd>f2</kbd>, etc; symbol keys (the likes of `#`, `@`, `*`, etc...)
generally use a name (`number_sign`, `at`, `asterisk`, etc...).

!!! tip

    If you want to test and discover all of the key names and combinations
    that will work, you may want to install
    [`textual-dev`](https://github.com/Textualize/textual-dev) and use the
    `textual keys` command.

    If you need help with keyboard bindings [please feel free to
    ask](index.md#questions-and-feedback).

## Local file system start location

By default Hike's local file system browser (the tree that appears in the
navigation panel) will always start out browsing the user's home directory.
If you prefer that it starts viewing somewhere else, you can change this
value in the configuration file.

```json
"local_start_location": "~",
```

For example, if you wanted it to always start with the current directory, you could change it to this:

```json
"local_start_location": ".",
```

## Main forge branches

When Hike looks for the README file of a repository in a git forge, by
default it first looks in the `main` branch and then as a backup in
`master`. If you wish to change this you can edit the list in the
configuration file.

For example: if you wanted to add `staging` and `production` to the list of
branches checked, you could change this:

```json
"main_branches": [
    "main",
    "master"
],
```

to be this:

```json
"main_branches": [
    "main",
    "master",
    "staging",
    "production"
],
```

## Markdown content types

When deciding what remote content is likely a Markdown document Hike
considers the following content types as good candidates:

- text/plain
- text/markdown
- text/x-markdown

If you wish to change this list you can edit this option in the
configuration file and add to the list:

```json
"markdown_content_types": [
    "text/plain",
    "text/markdown",
    "text/x-markdown"
],
```

## Markdown file extensions

By default Hike considers files with either a `.md` or a `.markdown`
extension to be Markdown files. If you wish to change that you can edit this
option in the configuration file.

For example, if you also wanted to recognise files with the `.mkdn`
extension as Markdown files, you could change this:

```json
"markdown_extensions": [
    ".md",
    ".markdown"
],
```

to be this:

```json
"markdown_extensions": [
    ".md",
    ".markdown",
    ".mkdn"
],
```

## Navigation panel

### Visibility

You can show or hide the navigation panel. This can be done in Hike with the
`Toggle Navigation` ([`ToggleNavigation`](#bindable-commands), bound to
<kbd>F2</kbd> by default) command.

!!! tip

    You can force navigation [visible](index.md#-navigation) or
    [hidden](index.md#-no-navigation) via [the command
    line](index.md#command-line-options).
    Note that this *also* configures the visibility of the navigation panel
    for future runs of Hike.

Here is Hike with the navigation panel visible:

```{.textual path="docs/screenshots/basic_app.py" title="Visible navigation panel" lines=40 columns=120 press="tab,d,ctrl+t"}
```

and with it hidden:

```{.textual path="docs/screenshots/basic_app.py" title="Hidden navigation panel" lines=40 columns=120 press="tab,d"}
```

### Location

When [visible](#visibility), the navigation panel can be located on the left
or the right of the screen; this is toggled using the `Change Navigation
Side` command ([`ChangeNavigationSide`](#bindable-commands), bound to
<kbd>Shift</kbd>+<kbd>F2</kbd> by default).

Here is Hike with the navigation panel visible on the right:

```{.textual path="docs/screenshots/basic_app.py" title="Navigation panel on the right" lines=40 columns=120 press="tab,d,ctrl+t,shift+f2"}
```

## Obsidian vaults location

The command for quickly browsing [Obsidian](https://obsidian.md) vaults in
the local filesystem will, by default, look in `~/Library/Mobile
Documents/iCloud~md~obsidian/Documents`.

!!! note

    I use Obsidian in the Apple ecosystem and use iCloud to sync my vaults; hence this default.

If you wish to change this to a default that makes sense for you, edit this
setting in the configuration file:

```json
"obsidian_vaults": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents",
```

## Theme

Hike has a number of themes available. You can select a theme using the
`Change Theme` ([`ChangeTheme`](#bindable-commands), bound to <kbd>F9</kbd>
by default) command. The available themes include:

```bash exec="on"
hike --theme=? | sed 's/^/- /'
```

!!! tip

    You can also [set the theme via the command line](index.md#-t-theme). This can
    be useful if you want to ensure that Hike runs up with a specific theme.
    Note that this *also* configures the theme for future runs of Hike.

Here's a sample of some of the themes:

```{.textual path="docs/screenshots/basic_app.py" title="textual-light" lines=40 columns=120 press="tab,d,ctrl+t,f9,t,e,x,t,u,a,l,-,l,i,g,h,t,enter"}
```

```{.textual path="docs/screenshots/basic_app.py" title="nord" lines=40 columns=120 press="tab,d,ctrl+t,f9,n,o,r,d,enter"}
```

```{.textual path="docs/screenshots/basic_app.py" title="catppuccin-latte" lines=40 columns=120 press="tab,d,ctrl+t,f9,c,a,t,p,p,u,c,c,i,n,-,l,a,t,t,e,enter"}
```

```{.textual path="docs/screenshots/basic_app.py" title="dracula" lines=40 columns=120 press="tab,d,ctrl+t,f9,d,r,a,c,u,l,a,enter"}
```

[//]: # (configuration.md ends here)
