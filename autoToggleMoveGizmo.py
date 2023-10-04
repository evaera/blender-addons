bl_info = {
    "name": "Auto Toggle Move Gizmo",
    "author": "evaera",
    "description": "Automatically toggles Move overlay when Transform Orientation is anything but Global",
    "blender": (3, 6, 0),
    "category": "3D View",
    "version": (1, 0)
}

import bpy
from bpy.app.handlers import persistent

@persistent
def show_gizmos_callback(scene):
    if scene.transform_orientation_slots[0].type == 'GLOBAL':
        show_gizmos = False
    else:
        show_gizmos = True

    areas = bpy.context.workspace.screens[0].areas

    for area in areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.show_gizmo_object_translate = show_gizmos


def register():
    pre_handlers = bpy.app.handlers.depsgraph_update_post
    # Add the callback to the depsgraph_update_pre handler
    pre_handlers.append(show_gizmos_callback)

def unregister():
    # Remove old versions of the callback from the depsgraph_update_pre handler
    pre_handlers = bpy.app.handlers.depsgraph_update_post
    for handler in list(pre_handlers):
        if handler.__name__ == "show_gizmos_callback":
            pre_handlers.remove(handler)
    

if __name__ == "__main__":
    register()