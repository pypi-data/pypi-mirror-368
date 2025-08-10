# Link Audit

LinkAudit – Superfast, simple, and deadly accurate to find broken links in markdown.

This `linkaudit` tool has the following features:

* Shows all external links (aka URLs) for a Shpinx or JupyterBook. Output is saved.
* Validate status of all discoverd external links for a Sphinx or Jupyterbook document. Output is saved.


## Installation

```
pip install linkaudit

```


## Usage

Linkaudit is a CLI tool.

To get help just run `linkaudit` without arguments.
```shell 
Linkaudit

Command 	: showlinks
Shows all URLs from MyST Markdown files in a directory and generates an HTML report.

Command 	: checklinks
Print txt tables of URLs checks of JB Book

Command 	: version
Prints the module version. Use [-v] [--v] [-version] or [--version].

Use linkaudit [COMMAND] --help for detailed help per command.
```

To use it on a  documentation created for `Jupyterbook` or `Sphinx`:

To show links, do:
```
linkaudit showlinks [DIRECTORY_TO_SPHINX or JUPYERBOOK files]
```

To check links, do:
```
linkaudit checklinks [DIRECTORY_TO_SPHINX or JUPYERBOOK files]
```

## Documentation
Full documentation is available at [https://nocomplexity.com/documents/linkaudit](https://nocomplexity.com/documents/linkaudit)

## License

This tool is licensed  GPL-3.0-or-later. 

