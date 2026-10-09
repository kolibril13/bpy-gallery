# Bpy Gallery

Welcome to this documentation! 👋  
Here, you’ll find a collection of curated examples for using Blender within Python notebooks.  
If you find these resources helpful, feel free to leave a star ⭐ on GitHub:  
[https://github.com/kolibril13/bpy-gallery](https://github.com/kolibril13/bpy-gallery)

## Repository layout

```
docs/
├── index.md, getting-started.md
├── basics/      # objects, materials, render engines, installing packages
├── databpy/     # point clouds, geometry nodes and attributes with databpy
├── typst/       # typst equations and code blocks
├── assets/      # .blend files and textures loaded by the notebooks
└── utils/
    └── gallery_utils.py   # fresh_scene(), render_result(), ASSETS
```

Each notebook starts with the same setup cell:

```python
import sys
from pathlib import Path

sys.path.append(str(Path.home() / "projects/bpy-gallery/docs/utils"))
from gallery_utils import ASSETS, fresh_scene, render_result
```
