# bustomize
customize+ to blender add-on ( aka **bustomize+** )

see: https://github.com/Aether-Tools/CustomizePlus

### INSTALLATION
download the latest release .zip and install the zip in blender 4.0+ thru `Edit > Preferences > Add-ons > Install...`

### USAGE
![GIF 9-2-2024 4-07-14 PM](https://github.com/user-attachments/assets/2a74c52a-f1ba-42c4-9d3d-47c07057ae53)

open the sidebar with `N` or `View > Sidebar`; in **object mode**, select a compatible xiv-exported armature (preferably one directly from textools), then paste in a copied template string from customize+.

the `bustomize` buttons will apply the template's scaling (or rotation+position) to each bone available in the target armature - this is done on **pose bones**, so you won't see any effects of this when in Edit Mode.

ctrl+Z can undo the change, and a button is included to reset any changes to the targeted armature after a c+ template has been applied.

caveats:
- rotation and position values from c+ templates are applied with their own button - their implementation is a little less straightforward than scale and may be unreliable
- application may behave strangely with nonstandard armatures such as those from devkits or skeleton resources. a toggle for axis flips is included, but it probably won't fix every case
- this add-on does **not** take into account racial scaling from xiv pbds -- the scaling will be applied consistently without regard for the target armature's race/gender. results necessarily won't be true-to-game, but they are close enough
- rotation+position application depends on the creation of dummy bones in the targeted armature; make sure to use the reset button to clean up these and reset parent-child relationships before any armature exporting
- rotation+position functionality is still very WIP and likely misses the mark, but it should give you a decent picture of possible clipping

### NOTES
7/21 note: several folks have reached out regarding usage of bustomize to create face sculpt mods. this does not work and is not endorsed - bustomize is not to be used with exporting meshes, and to do so would require applying the posed armature modifier and re-applying all involved weights. it's not a good idea!

this project is not maintained or endorsed by the developers of customize+ -- it also depends entirely on them and their architecture, so please give them some love

add-on made with blender_vscode by jacques lucke: https://github.com/JacquesLucke/blender_vscode

for support: reach out to me on [bsky](https://bsky.app/profile/bwuny.heliosphe.re)
