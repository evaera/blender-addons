bl_info = {
    "name": "Distribute Points along Curve",
    "blender": (4, 1, 0),
    "category": "Object",
    "description": "Scale and distribute control points of a curve (NURBS and Bezier) along selected axes",
}

import bpy

class CURVE_OT_distribute_points_along_curve(bpy.types.Operator):
    """Scale and distribute selected points on a curve"""
    bl_idname = "curve.distribute_points_along_curve"
    bl_label = "Distribute Points along Curve"
    bl_options = {'REGISTER', 'UNDO'}
    
    lock_x: bpy.props.BoolProperty(name="Lock X", default=True)
    lock_y: bpy.props.BoolProperty(name="Lock Y", default=True)
    lock_z: bpy.props.BoolProperty(name="Lock Z", default=False)

    distribution_mode: bpy.props.EnumProperty(
        name="Distribution Mode",
        description="How to distribute the points",
        items=[
            ('PROJECT', "Project", "Project points along the original curve"),
            ('SPREAD', "Spread", "Distribute points proportionally"),
            ('SPREAD_EVENLY', "Spread Evenly", "Distribute points evenly along the length")
        ],
        default='SPREAD'
    )
    
    def execute(self, context):
        obj = context.object
        if obj.type != 'CURVE':
            self.report({'WARNING'}, "Selected object is not a curve.")
            return {'CANCELLED'}
        
        spline = obj.data.splines[0]
        
        if spline.type not in {'NURBS', 'BEZIER'}:
            self.report({'WARNING'}, "Curve type not supported.")
            return {'CANCELLED'}
        
        points = spline.points if spline.type == 'NURBS' else spline.bezier_points
        
        first_point = points[0]
        last_point = points[-1]
        
        start = first_point.co.xyz
        end = last_point.co.xyz

        total_length = sum((points[i+1].co.xyz - points[i].co.xyz).length
                           for i in range(len(points) - 1))
        
        if self.distribution_mode == 'PROJECT':
            for point in points[1:-1]:
                direction = (end - start).normalized()
                distance = (point.co.xyz - start).dot(direction)
                projected = start + direction * distance
                if not self.lock_x:
                    point.co.x = projected.x
                if not self.lock_y:
                    point.co.y = projected.y
                if not self.lock_z:
                    point.co.z = projected.z
        
        elif self.distribution_mode == 'SPREAD_EVENLY':
            num_points = len(points) - 1
            for i, point in enumerate(points[1:-1], 1):
                factor = i / num_points
                new_position = start.lerp(end, factor)
                if not self.lock_x:
                    point.co.x = new_position.x
                if not self.lock_y:
                    point.co.y = new_position.y
                if not self.lock_z:
                    point.co.z = new_position.z
        
        elif self.distribution_mode == 'SPREAD':
            for i, point in enumerate(points[1:-1], 1):
                distance = sum((points[j+1].co.xyz - points[j].co.xyz).length
                               for j in range(i))
                proportion = distance / total_length
                if not self.lock_x:
                    point.co.x = start.x + proportion * (end.x - start.x)
                if not self.lock_y:
                    point.co.y = start.y + proportion * (end.y - start.y)
                if not self.lock_z:
                    point.co.z = start.z + proportion * (end.z - start.z)

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CURVE_OT_distribute_points_along_curve.bl_idname, text="Distribute Points along Curve")

def register():
    bpy.utils.register_class(CURVE_OT_distribute_points_along_curve)
    bpy.types.VIEW3D_MT_edit_curve.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CURVE_OT_distribute_points_along_curve)
    bpy.types.VIEW3D_MT_edit_curve.remove(menu_func)

if __name__ == "__main__":
    register()
