import bpy

# アドオン情報
bl_info = {
    "name": "LevelEditor",
    "author": "Takuto Yamaguchi",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "",
    "description": "LevelEditor",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

# モジュールのインポート
from .stretch_vertex import MYADDON_OT_stretch_vertex
from .create_ico_sphere import MYADDON_OT_create_ico_sphere
from .add_file_name import MYADDON_OT_add_filename
from .export_scene import MYADDON_OT_export_scene
from .my_menu import TOPBAR_MT_my_menu
from .file_name import OBJECT_PT_file_name
from .add_cllider import MYADDON_OT_add_collider
from .collider import OBJECT_PT_collider
from .draw_collider import DrawCollider
from .add_disable_flag import MYADDON_OT_add_disable_flag
from .add_disable_flag import OBJECT_PT_disable_flag
from .spawn import MYADDON_OT_spawn_symbol_import
from .spawn import MYADDON_OT_spawn_symbol_create
    
# Blenderに登録するクラスリスト
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
    MYADDON_OT_add_filename,
    OBJECT_PT_file_name,
    MYADDON_OT_add_collider,
    OBJECT_PT_collider,
    MYADDON_OT_add_disable_flag,
    OBJECT_PT_disable_flag,
    MYADDON_OT_spawn_symbol_import,
    MYADDON_OT_spawn_symbol_create,
)


# メニュー項目描画
def draw_menu_manual(self, context):

    self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

# AddonEnabledCallback
def register():
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    # blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    #3Dビューに描画関数を追加
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider, (), "WINDOW", "POST_VIEW")
    print("LevelEditor Enabled")

# AddonDisabledCallback
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    # blenderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)

    #3Dビューから描画関数を削除
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, "WINDOW")
    
    print("LevelEditor Disabled")
    
    
# testCode
if __name__ == "__main__":
    register()
 