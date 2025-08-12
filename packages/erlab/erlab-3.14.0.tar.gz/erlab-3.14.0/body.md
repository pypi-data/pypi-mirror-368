## v3.14.0 (2025-08-12)

### ✨ Features

- **imagetool:** add cursor color customization ([c90b52d](https://github.com/kmnhan/erlabpy/commit/c90b52de2ac36d0007a297a943a983e4b1983aaf))

  Adds a new dialog that can be used to customize the colors of cursors in the ImageTool. This allows users to set specific colors for each cursor, and also allows sampling cursor colors from colormaps.

- **imagetool:** add toggle action for cursor visibility ([c2a6640](https://github.com/kmnhan/erlabpy/commit/c2a6640c6b3a80472f1420fdadc07c926896c498))

  Allows users to toggle the visibility of cursors. The new action is located in the View menu, and can be accessed with the keyboard shortcut `Shift + V`.

- **plotting.bz:** add `plot_bz` function for plotting arbitrary 2D Brillouin zones given the basis vectors ([11fa5a8](https://github.com/kmnhan/erlabpy/commit/11fa5a8c9bd619e0d22801e2c29076cd02d589de))

- **interactive:** implement user customization options for interactive tools ([6af26f3](https://github.com/kmnhan/erlabpy/commit/6af26f398fff6d747cc5794c5bf35851f885b4be))

  Users can now customize various default settings related to ImageTool, such as the default cursor color and colormap. The options can be modified from a new preference menu option in the menu bar of ImageTool and ImageTool manager. The changes are saved and restored across sessions.

### 🐞 Bug Fixes

- **imagetool:** fixes cursor removal resulting in incorrect autorange behavior ([240c29e](https://github.com/kmnhan/erlabpy/commit/240c29e11eebdd59707a2004b0b6fb9529b1fcca))

- **imagetool:** fix selection of cropped data with manual limits ([55cd311](https://github.com/kmnhan/erlabpy/commit/55cd31194ff62c4cb59fbfb8059eb0060f099d57))

- **io.plugins.erpes:** fix loading incomplete 2-motor scan ([6de4558](https://github.com/kmnhan/erlabpy/commit/6de45585a4e61ba571c3a45db85f25793b3b0930))

  Fixes an issue where incomplete 2-motor scans with nan values in datetime coordinates failed to load.

- **interactive.colors:** automatically load all colormaps when given cmap is not found ([7bdf47d](https://github.com/kmnhan/erlabpy/commit/7bdf47df4bc8e2b775ae045f9680ac0afc604169))

### ♻️ Code Refactor

- **imagetool:** improve robustness of dialog management ([f23bfda](https://github.com/kmnhan/erlabpy/commit/f23bfda193726b68c6ebf00ee84903f6ab978386))

  Contains some internal changes to dialog creation and garbage collection, avoiding `exec()`. Users should not notice any difference in functionality.

- **plotting.annotations:** enhance `mark_points` function with additional options ([84e80a1](https://github.com/kmnhan/erlabpy/commit/84e80a19625ddd3f91b87d556af8938835b5d558))

- **interactive:** include stack trace in error dialogs for better debugging ([1c59997](https://github.com/kmnhan/erlabpy/commit/1c599971382d9be95303f01372e8ab7f30a47794))

- **plotting.annotations:** remove seldom used `label_subplots_nature` function ([28150fc](https://github.com/kmnhan/erlabpy/commit/28150fc19b1197aa151a0ee57b862b45528c88e5))

- remove unused private functions ([59734d1](https://github.com/kmnhan/erlabpy/commit/59734d1a2b23a33b4dde8703a3c950d38041fb06))

- **io.utils:** deprecate wrapper functions for xarray I/O ([a1d740b](https://github.com/kmnhan/erlabpy/commit/a1d740b3e6ee4597a3646e566585341e82e5b3ec))

  Deprecates `open_hdf5`, `load_hdf5`, `save_as_hdf5`, and `save_as_netcdf` in favor of direct xarray methods. Use `xarray.open_dataarray` and `xarray.DataArray.to_netcdf` directly for better compatibility and performance.

[main 5dfcb6a] bump: version 3.13.0 → 3.14.0
 3 files changed, 3 insertions(+), 3 deletions(-)

