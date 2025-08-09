# Ecdysys
[![](https://img.shields.io/github/v/release/claymorwan/ecdysys)](https://GitHub.com/claymorwan/ecdysys)

Little CLI tool to print and update system
Currently supported package managers are:
- `pacman` (requires `pacman-contrib` as well)
- `yay` and `paru` (aur support)
- `dnf`
- `flatpak`

## Installation
### From Pypi
```shell
pip install ecdysys
```
### From the Aur
```shell
paru -S python-ecdysys
```
2. Create a `config.toml` file, these are the following entry available

| Entry                    | Usage                                                     | Valid entry                                           | Example                       |
|--------------------------|-----------------------------------------------------------|-------------------------------------------------------|-------------------------------|
| `pkg_managers`*          | package manager to use                                    | any of the supported package manager (list of string) | `[ "pacman", "flatpak" ]`     |
| `aur_helper`             | aur helper to use (`pacman` must be set in `pkg_managers` | any of the supported aur helper (string)              | `"paru"`                      |
| `post_install_script`    | path to script ot run after installation                  | path to file (string)                                 | `path/to/script`              |
| `args_<package manager>` | arguments for any of the selected package manager         | string                                                | `args_pacman = "--noconfirm"` |
| `sudobin`                | sudobin executable ame or path                            | string                                                | `sudo-rs`; `/usr/bin/sudo-rs` |

*Must be set

## Usage
```
usage: ecdysys [-h] [-v] [-l] [-u] [--no-spinner]

Python CLI to update your system packages

options:
  -h, --help     show this help message and exit
  -v, --version  Print version
  -l, --list     List available updates
  -u, --update   Update package
  --no-spinner   Doesn't show spinner when listing updates
```
