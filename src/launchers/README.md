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

## logic

### plugins

Loading of plugins is performed via a "hack". We fully override autoloading
of plugins from the user preferences.

The autoloading of plugins is stored in the `pluginPrefs.mel` file, located in the
user preferences. At start-up we replace this file by a pre-defined one, which
maya will read just fine.

The only issue is if you don't have any user preferences yet, because it's the
first time you are launching maya on your machine, or if it is the first time maya
is launched for the given user preferences location. In that case the hack will not
work on the first time, and you will need to restart maya righ after.
(This is suggested to the user via a small dialog)


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