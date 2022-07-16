I recently bought some low-poly models from [Synty](https://syntystore.com/), but importing those models into Blender proved to be a bit of a headache. Once I finally figured out the necessary cleanup steps, I decided to write this tool to automate the process.

This repo contains a Blender Addon that adds a new "Synty FBX" option to the import menu. It also contains a batch wrapper script that is capable of converting `.fbx` to `.blend` en-masse.

## Running as a Blender addon
If you only need to import a single model, you can open `synty_character_fixer.py` in a Text Editor window (or simply copy-paste its contents) and hit "Run Script". This will add a "Synty FBX (.fbx)" option to the import menu, but it will not persist when you restart Blender.

For a more permanent installation, go to `Edit` > `Preferences...` > `Add-ons` and click `Install...`. Choose `synty_character_fixer.py`, and then enable the addon. If you decide you no longer need this addon, you can disable it from the same screen.

## Running in batch mode
1. Before running, note that Blender must be on your `PATH`.
2. Usage:
```
usage: batch_converter.py [-h] [--out-dir OUT_DIR] [--verbose] [--overwrite] files [files ...]

positional arguments:
  files              Files to convert

optional arguments:
  -h, --help         show this help message and exit
  --out-dir OUT_DIR  Output directory. Defaults to same directory as input file.
  --verbose          Enable verbose log output
  --overwrite        Overwrite existing output
```

## Notes
- There a couple heuristics and assumptions in here around file and directory names. This script has worked for every example I have tried, but there may be some model packs that use different naming conventions or directory structure. Feel free to submit a PR if you find anything like this.
- Before importing models, I had to use the [Autodesk FBX Converter](https://www.autodesk.com/developer-network/platform-technologies/fbx-converter-archives) tool to convert the models from ASCII FBX to Binary FBX, since Blender cannot import the ASCII-based format.
- Most Synty models come with multiple variant textures. This tool only loads the default texture.
