from maya import cmds

cmds.optionVar(intValue=("showHomeScreenOnStartup", 0))
cmds.optionVar(intValue=("viewCubeShowCube", 0))
cmds.optionVar(intValue=("SafeModeUserSetupHashOption", 0))

cmds.undoInfo(state=True, infinity=True)
cmds.optionVar(intValue=("undoIsInfinite", 1))

# Disable the Save UI layout from scene
cmds.optionVar(intValue=("useSaveScenePanelConfig", 0))
# Disable the Load UI layout from scene
cmds.optionVar(intValue=("useScenePanelConfig", 0))

# cmds.optionVar(intValue=("isIncrementalSaveEnabled", 1))
# cmds.optionVar(intValue=("RecentBackupsMaxSize", 10 ))

cmds.optionVar(intValue=("RecentFilesMaxSize", 10))
cmds.optionVar(intValue=("RecentProjectsMaxSize", 10))

# default framerange
cmds.optionVar(intValue=("playbackMaxDefault", 1200))
cmds.optionVar(intValue=("playbackMaxRangeDefault", 1120))
cmds.optionVar(intValue=("playbackMinDefault", 1001))
cmds.optionVar(intValue=("playbackMinRangeDefault", 1001))

# Disable the copy/paste "functionality" of Maya that wreaks havoc
# WARNING: raise error, I don't know why. To put last.
cmds.hotkeySet("NoCopyPaste", current=True)
cmds.hotkey(keyShortcut="c", ctrlModifier=True, name="")
cmds.hotkey(keyShortcut="v", ctrlModifier=True, name="")
