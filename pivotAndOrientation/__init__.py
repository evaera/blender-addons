import bpy

custom_transforms = []
addon_keymaps = []

def set_gizmos(show_gizmos):
    for area in bpy.context.workspace.screens[0].areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.show_gizmo_object_translate = show_gizmos

class OBJECT_OT_set_pivot(bpy.types.Operator):
    bl_idname = "object.set_pivot"
    bl_label = "Set Pivot"
    bl_description = "Set the pivot point"

    pivot_type: bpy.props.EnumProperty(
        items=[
            ('BOUNDING_BOX_CENTER', "Bounding Box Center", ""),
            ('CURSOR', "3D Cursor", ""),
            ('INDIVIDUAL_ORIGINS', "Individual Origins", ""),
            ('MEDIAN_POINT', "Median Point", ""),
            ('ACTIVE_ELEMENT', "Active Element", ""),
        ],
        name="Pivot Type",
        description="Choose the pivot point type",
        default='MEDIAN_POINT'
    )

    def execute(self, context):
        context.scene.tool_settings.transform_pivot_point = self.pivot_type
        return {'FINISHED'}

class OBJECT_OT_set_transform_orientation(bpy.types.Operator):
    bl_idname = "object.set_transform_orientation"
    bl_label = "Set Transform Orientation"
    bl_description = "Set the transform orientation"

    orientation_type: bpy.props.StringProperty(
        name="Orientation Type",
        description="Choose the transform orientation type",
        default="GLOBAL"
    )

    def execute(self, context):
        context.scene.transform_orientation_slots[0].type = self.orientation_type

        if context.preferences.addons[__name__].preferences.show_gizmo_on_non_global:
            set_gizmos(self.orientation_type != 'GLOBAL')

        return {'FINISHED'}

class OBJECT_OT_delete_custom_orientations(bpy.types.Operator):
    bl_idname = "object.delete_custom_orientations"
    bl_label = "Delete Custom Orientations"
    bl_description = "Delete all custom transform orientations"

    def execute(self, context):
        slots = context.scene.transform_orientation_slots
        for transform in custom_transforms:
            slots[0].type = transform
            bpy.ops.transform.delete_orientation()
        custom_transforms.clear()
        return {'FINISHED'}

class VIEW3D_MT_PivotAndOrientationMenu(bpy.types.Menu):
    bl_label = "Pivot and Orientation"
    bl_idname = "VIEW3D_MT_pivot_and_orientation_menu"

    def draw(self, context):
        layout = self.layout

        num_columns = 2 if not custom_transforms else 3
        split_factor = 1.0 / num_columns

        split = layout.split(factor=split_factor)

        col_pivot = split.column()
        col_pivot.operator("object.set_pivot", text="Bounding Box", icon='PIVOT_BOUNDBOX').pivot_type = 'BOUNDING_BOX_CENTER'
        col_pivot.operator("object.set_pivot", text="3D Cursor", icon='PIVOT_CURSOR').pivot_type = 'CURSOR'
        col_pivot.operator("object.set_pivot", text="Individual Origins", icon='PIVOT_INDIVIDUAL').pivot_type = 'INDIVIDUAL_ORIGINS'
        col_pivot.operator("object.set_pivot", text="Median Point", icon='PIVOT_MEDIAN').pivot_type = 'MEDIAN_POINT'
        col_pivot.operator("object.set_pivot", text="Active Element", icon='PIVOT_ACTIVE').pivot_type = 'ACTIVE_ELEMENT'
        col_pivot.separator()
        col_pivot.prop(context.scene.tool_settings, "use_transform_data_origin", text="Only Origins")
        col_pivot.prop(context.scene.tool_settings, "use_transform_pivot_point_align", text="Only Locations")

        col_orientation = split.column()

        orientation_icons = {
            'GLOBAL': 'ORIENTATION_GLOBAL',
            'LOCAL': 'ORIENTATION_LOCAL',
            'NORMAL': 'ORIENTATION_NORMAL',
            'GIMBAL': 'ORIENTATION_GIMBAL',
            'VIEW': 'ORIENTATION_VIEW',
            'CURSOR': 'ORIENTATION_CURSOR',
            'PARENT': 'ORIENTATION_PARENT'
        }

        builtin_transforms = ['GLOBAL', 'LOCAL', 'NORMAL', 'GIMBAL', 'VIEW', 'CURSOR', 'PARENT']
        for orientation in builtin_transforms:
            col_orientation.operator(
                "object.set_transform_orientation",
                text=orientation.title(),
                icon=orientation_icons[orientation]
            ).orientation_type = orientation

        col_orientation.operator("transform.create_orientation", text="Create", icon='ADD').use = True

        if custom_transforms:
            col_custom = split.column()
            col_custom.label(text="Custom Orientations:")
            for transform in custom_transforms:
                col_custom.operator(
                    "object.set_transform_orientation",
                    text=transform,
                    icon='ORIENTATION_NORMAL'
                ).orientation_type = transform
            col_custom.separator()
            col_custom.operator("object.delete_custom_orientations", text="Delete All", icon='TRASH')

class OBJECT_OT_show_pivot_orientation_menu(bpy.types.Operator):
    bl_idname = "object.show_pivot_orientation_menu"
    bl_label = "Show Pivot and Orientation Menu"
    bl_description = "Show menu for pivot and transform orientation settings"

    def execute(self, context):
        global custom_transforms

        builtin_transforms = ['GLOBAL', 'LOCAL', 'NORMAL', 'GIMBAL', 'VIEW', 'CURSOR', 'PARENT']
        try:
            context.scene.transform_orientation_slots[0].type = ""
        except Exception as inst:
            transforms = str(inst).split("'")[1::2]

        custom_transforms = [t for t in transforms if t not in builtin_transforms]

        bpy.ops.wm.call_menu(name=VIEW3D_MT_PivotAndOrientationMenu.bl_idname)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator("object.show_pivot_orientation_menu", text="Pivot and Orientation Menus")

class PivotOrientationPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_gizmo_on_non_global: bpy.props.BoolProperty(
        name="Show Move Gizmo on Non-Global Orientations",
        description="Show Move Gizmo when orientation is not global, so that you can visually see which axes are which",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_gizmo_on_non_global")

def register():
    bpy.utils.register_class(PivotOrientationPreferences)
    bpy.utils.register_class(OBJECT_OT_set_pivot)
    bpy.utils.register_class(OBJECT_OT_set_transform_orientation)
    bpy.utils.register_class(OBJECT_OT_delete_custom_orientations)
    bpy.utils.register_class(VIEW3D_MT_PivotAndOrientationMenu)
    bpy.utils.register_class(OBJECT_OT_show_pivot_orientation_menu)
    bpy.types.VIEW3D_MT_view.append(menu_func)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(OBJECT_OT_show_pivot_orientation_menu.bl_idname, type='FOUR', value='PRESS')
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(PivotOrientationPreferences)
    bpy.utils.unregister_class(OBJECT_OT_set_pivot)
    bpy.utils.unregister_class(OBJECT_OT_set_transform_orientation)
    bpy.utils.unregister_class(OBJECT_OT_delete_custom_orientations)
    bpy.utils.unregister_class(VIEW3D_MT_PivotAndOrientationMenu)
    bpy.utils.unregister_class(OBJECT_OT_show_pivot_orientation_menu)
    bpy.types.VIEW3D_MT_view.remove(menu_func)

    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
