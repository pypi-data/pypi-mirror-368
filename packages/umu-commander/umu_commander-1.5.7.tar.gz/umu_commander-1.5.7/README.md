## umu-commander
### umu-commander is an interactive CLI tool to augment umu-launcher as well as help you manage its Proton versions.

Proton versions can track and untrack directories, with the intention of safely removing them once no game depends on one.

Vanilla umu config files currently (06/2025) do not support setting environmental variables. This tool adds such functionality with an extra TOML table within said configs, see `example_config.toml` for an example.

### Config
The configuration file lives at `~/.config/umu-commander.toml`, which cannot be changed as of now. You can generate one by running the app by itself.

The config schema is as follows:

| Name                      | Description                                                        |
|:--------------------------|:-------------------------------------------------------------------|
| `PROTON_PATHS`            | List of directories umu-commander will search for Proton versions. |
| `UMU_PROTON_PATH`         | Directory where umu-launcher downloads its UMU-Proton versions.    |
| `DB_NAME`                 | Tracking DB filename.                                              |
| `DB_DIR`                  | Directory where the Tracking DB is stored.                         |
| `UMU_CONFIG_NAME`         | Name of the umu config created using umu-commander create.         |
| `DEFAULT_PREFIX_DIR`      | Directory where umu-commander will search for WINE prefixes.       |
| `[DLL_OVERRIDES_OPTIONS]` | TOML table where all possible DLL overrides are listed.            |

To add an extra DLL override option, add a line below the table in the form "`Label`" = "`WINE override string`". Use the winhttp example as a template.

### Verbs
umu-commander needs one of the following verbs specified after the executable name:

| Name      | Description                                                                                                                                                                                                                                                                  |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `track`   | Tracks current directory with the selected Proton version.<br/>Also removes it from any other tracking lists.                                                                                                                                                                |
| `untrack` | Removes the current directory from all tracking lists.                                                                                                                                                                                                                       |
| `users`   | Lists which directories the selected Proton version is tracking.                                                                                                                                                                                                             |
| `delete`  | Interactively deletes Proton versions that are currently tracking nothing.<br/>Will not remove the latest UMU-Proton and Proton versions that haven't been used for tracking before.<br/>umu-commander will never delete anything without invoking this verb and confirming. |
| `create`  | Creates an augmented umu config in the current directory.<br/>These configs are compatible with vanilla umu-launcher, although the DLL override functionality won't work.                                                                                                    |
| `run`     | Runs a program using the umu config in the current directory.                                                                                                                                                                                                                |

### Installation/Usage
Add umu-run to your PATH and then install with pipx by running `pipx install umu-commander`. After that you can use umu-commander by running `umu-commander <verb>`. 

### Return codes
| Number | Name                | Description                                                     |
|:-------|:--------------------|:----------------------------------------------------------------|
| 0      | `SUCCESS`           | Program executed as intended.                                   |
| 1      | `DECODING_ERROR`    | Failed to parse a file.                                         |
| 2      | `INVALID_SELECTION` | User selected an invalid verb or there are no valid selections. |
