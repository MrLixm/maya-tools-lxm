# launchers

Custom scripts to launch Maya with a specific configuration.

Execution diagram :

```shell
"launcher.Maya-2023.env-default.sh"
∣ setup environment variables
∣ start maya
↳    "startup/userSetup.py"
     ∣ override python logger
     ∣ setup preferences
     ↳    "env-default/userPrefs.py"
          # personal preferences to toggle
     ∣ setup plugins
     ↳    "env-default/pluginPrefs.mel"
          # plugin autoloading
```

## structure

### `startup/`

Agnostic files. Can be launched for any version and any configuration.
Registered in `PYTHONPATH`.

### `prefs/` 

Where user maya preferences are stored. This is an example, but they could
be set anywhere, or not even set, and you could use the default ones.

### `env-XXX` 

Interchangeable directory to "customize" maya behavior. Set via `LXM_MAYA_ENV_DIR`
and then used in `startup/userSetup.py`.

You can find an example with the `env-default` directory.