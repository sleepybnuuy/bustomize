# bustomize
customize+ to blender plugin

### INSTALLATION
download the latest release .zip and install the zip in blender 4.0+ thru `Edit > Preferences > Add-ons > Install...`

### USAGE
![GIF 9-2-2024 4-07-14 PM](https://github.com/user-attachments/assets/2a74c52a-f1ba-42c4-9d3d-47c07057ae53)

select a compatible xiv-exported armature (preferably one directly from textools), then paste in a copied template string from customize+.

the `do bustomize` button will apply the template's scaling to each bone available in the target armature - this is done on **pose bones**, so you won't see any effects of this when in Edit Mode.

ctrl+Z can undo the change, and a button is included to reset any scaling & bone parenting changes to the targeted armature after a c+ scale has been applied.

caveats:
- rotation and position values from c+ templates are currently ignored because i'm lazy
- scaling may behave strangely with nonstandard armatures such as those from devkits or skeleton resources. a toggle for axis flips is included, but it probably won't fix every case
- this add-on does **not** take into account racial scaling from xiv pbds -- the scaling will be applied consistently without regard for the target armature's race/gender. results necessarily won't be true-to-game, but they are close enough

### NOTES
this project is not maintained or endorsed by the developers of customize+ -- please visit their repo here: https://github.com/Aether-Tools/CustomizePlus

add-on made with blender_vscode by jacques lucke: https://github.com/JacquesLucke/blender_vscode
