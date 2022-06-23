import bpy, mathutils

bl_info = {
    "name": "Acceleration to Animation",
    "author": "Giles Barton-Owen",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Edit > Accel To Animation",
    "description": "Bake the transforms from an acceleration object to the active object",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Animation",
}

class Accel_to_anim_props(bpy.types.PropertyGroup):

    accel_object: bpy.props.PointerProperty(
        type=bpy.types.Object
    )
    vel_object: bpy.props.PointerProperty(
        type=bpy.types.Object
    )
    
    

PROP_ACCEL_NAME = "ACCELTOANIM_ACCEL_OBJ"
PROP_VEL_NAME = "ACCELTOANIM_VEL_OBJ"
PROP_PARENT_NAME = "ACCELTOANIM_PARENT_OBJ"



def do_vel_pos_for(accel,vel, target, context=None):
    scene = bpy.context.scene
    startf = scene.frame_start
    endf = scene.frame_end
    
    fps = scene.render.fps
    dt = 1.0 / fps
    scene.frame_set(startf-1)
    
    if vel is None:
        vmat = mathutils.Matrix.Identity(4)
    else:
        vmat = vel.matrix_world.copy()
    tmat = target.matrix_world.copy()
    vpos = vmat.to_translation()
    veuler = vmat.to_euler()
    vscale = vmat.to_scale()
    
    tpos = tmat.to_translation()
    teul = tmat.to_euler()
    tscale = tmat.to_scale()
    
    if context:
        context.window_manager.progress_begin(startf, endf*2)
    set_last_frame=True
    for i in range(startf, endf):
        if context:
            context.window_manager.progress_update(i)
        if vel:
            try:
                vel.keyframe_delete('location', frame=i)
                vel.keyframe_delete('rotation_euler', frame=i)
            except RuntimeError as e:
                pass
        try:
            target.keyframe_delete('location', frame=i)
            target.keyframe_delete('rotation_euler', frame=i)
        except RuntimeError as e:
                pass
        
        scene.frame_set(i)
        amatrix = accel.matrix_world.copy()
        apos = amatrix.to_translation()
        ascale = amatrix.to_scale()
        aeuler = amatrix.to_euler()
        
        no_accel = all(abs(p) < 0.001 for p in apos) and all(abs(r) < 0.001 for r in aeuler)
        
        def update_target():
            nonlocal tpos
            vpos_r = vpos.copy()
            vpos_r.rotate(teul)
            tpos += vpos_r * dt
            for j in range(len(teul[:])):
                teul[j] += veuler[j]*dt
        
        if no_accel and i != scene.frame_end-1:
            # update position with velocity
            update_target()
            set_last_frame=False
        else:
            # update previous position keyframe if set_last_frame = False
            if not set_last_frame:
                tmat = mathutils.Matrix.LocRotScale(tpos, teul, tscale)
                target.matrix_world=tmat
                #print(f"Inserting keyframe at {i}")
                target.keyframe_insert('location', frame=i-1, options={'INSERTKEY_NEEDED'})
                target.keyframe_insert('rotation_euler', frame=i-1, options={'INSERTKEY_NEEDED'})
                if vel is not None:
                    vel.matrix_world=vmat
                    #print(f"Inserting keyframe at {i}")
                    vel.keyframe_insert('location', frame=i-1, options={'INSERTKEY_NEEDED'})
                    vel.keyframe_insert('rotation_euler', frame=i-1, options={'INSERTKEY_NEEDED'})
            
            # Update velocity
            vpos += apos * dt
            for j in range(len(veuler[:])):
                veuler[j] += aeuler[j]*dt
                
            vmat = mathutils.Matrix.LocRotScale(vpos, veuler, vscale)
            if vel is not None:
                vel.matrix_world=vmat
                #print(f"Inserting keyframe at {i}")
                vel.keyframe_insert('location', frame=i, options={'INSERTKEY_NEEDED'})
                vel.keyframe_insert('rotation_euler', frame=i, options={'INSERTKEY_NEEDED'})

        
            # Update position
            update_target()
                
            new_tmat = mathutils.Matrix.LocRotScale(tpos, teul, tscale)
            target.matrix_world=new_tmat
            #print(f"Inserting keyframe at {i}")
            target.keyframe_insert('location', frame=i, options={'INSERTKEY_NEEDED'})
            target.keyframe_insert('rotation_euler', frame=i, options={'INSERTKEY_NEEDED'})
            set_last_frame=True
    
    fs = target.animation_data.action.fcurves
    for f in fs:
        if context:
            context.window_manager.progress_update(i+endf)
        if f.data_path in ['location', 'rotation_euler']:
            for kf in f.keyframe_points:
                kf.interpolation = 'LINEAR'
    
    if context:
        context.window_manager.progress_end()
        
        



def do_accel_to_anim(context):
    sel_objs = context.selected_objects
    active = context.active_object
    err = False
    if PROP_ACCEL_NAME in active:
        accel = bpy.data.objects[active[PROP_ACCEL_NAME]]
        if PROP_VEL_NAME in active:
            vel = bpy.data.objects[active[PROP_VEL_NAME]]
        else:
            vel= None
    elif PROP_PARENT_NAME in active:
        nactive = bpy.data.objects[active[PROP_PARENT_NAME]]
        accel = bpy.data.objects[nactive[PROP_ACCEL_NAME]]
        if PROP_VEL_NAME in active:
            vel = bpy.data.objects[nactive[PROP_VEL_NAME]]
        else:
            vel= None
        active = nactive
    else:
        err = True
    # else:
    #     accel = [o for o in sel_objs if o.name.startswith('Accel') and o is not active]
    #     if len(accel) < 1:
    #         err = True
    #         print('Please select an object with name starting with "Accel"')
    #     else:
    #         accel = accel[0]
    #     vel = [o for o in sel_objs if o.name.startswith('Vel')]
    #     if len(vel) < 1:
    #         vel=None
    #     else:
    #         vel = vel[0]
    if not err:
        do_vel_pos_for(accel, vel, active, context=context)
        

def setup_accel_to_anim(context):
    sel_objs = context.selected_objects
    active = context.active_object
    err = False
    accel = context.scene.accel_to_anim.accel_object
    vel = context.scene.accel_to_anim.vel_object

    if not err:
        active[PROP_ACCEL_NAME] = accel.name
        accel[PROP_PARENT_NAME] = active.name
        if vel is not None:
            active[PROP_VEL_NAME] = vel.name
            vel[PROP_PARENT_NAME] = active.name


class Accel_to_Anim_PT_Acceleartion_to_Animation_Panel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Accel To Animation"
    bl_category = 'Edit'
    bl_idname = "VIEW_PT_accel_to_anim_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        layout.label(text="Bake:")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.accel_to_anim")
        
        # Big render button
        layout.label(text="Setup:")
        layout.prop(context.scene.accel_to_anim, 'accel_object')
        layout.prop(context.scene.accel_to_anim, 'vel_object')

        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.accel_to_anim_setup", text="Setup for active")
        
        

class Accel_to_Anim_OT_Acceleartion_to_Animation_setup(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.accel_to_anim_setup"
    bl_label = "Setup accel_to_anim"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.scene.accel_to_anim.accel_object is not None

    def execute(self, context):
        setup_accel_to_anim(context)
        return {'FINISHED'}

class Accel_to_Anim_OT_Acceleartion_to_Animation(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.accel_to_anim"
    bl_label = "Accel to animation"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        do_accel_to_anim(context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(Accel_to_Anim_OT_Acceleartion_to_Animation.bl_idname, text=Accel_to_Anim_OT_Acceleartion_to_Animation.bl_label)

classes = [
    Accel_to_Anim_OT_Acceleartion_to_Animation_setup,
    Accel_to_Anim_OT_Acceleartion_to_Animation,
    Accel_to_Anim_PT_Acceleartion_to_Animation_Panel,
    Accel_to_anim_props
]

# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.accel_to_anim = bpy.props.PointerProperty(type=Accel_to_anim_props)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.object.simple_operator()


        
