bl_info = {
    "name": "Auto Collection Instance Offset",
    "author": "evaera",
    "description": "Automatically sets collections' instance offset property based on member objects",
    "blender": (3, 6, 0),
    "category": "3D View",
    "version": (1, 0),
}

import bpy
from bpy.app.handlers import persistent


@persistent
def set_instance_offset(scene):
    for collection in bpy.data.collections:
        if "Manual Offset" in collection and collection["Manual Offset"] == True:
            continue

        root = None

        for object in collection.objects:
            if object.type != "MESH" and object.type != "EMPTY":
                continue
            if object.parent == None:
                root = object
                break

        if not root:
            continue

        collection.instance_offset = root.location


def register():
    post_handlers = bpy.app.handlers.depsgraph_update_post
    post_handlers.append(set_instance_offset)


def unregister():
    post_handlers = bpy.app.handlers.depsgraph_update_post
    post_handlers.remove(set_instance_offset)


if __name__ == "__main__":
    register()
