import bpy
import math

# blenderRegisterAddonInfo
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


# オペレータ 頂点を伸ばす
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"
    # redo undo 可能オプション
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれるコールバック関数
    def execute(self, context):
        bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
        print("頂点を伸ばしました。")

        # オペレータの命令終了を通知
        return {'FINISHED'}
    

# オペレータ ICO球の作成
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_ico_sphere"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        print("ICO球を生成しました。")

        return {'FINISHED'}
    

# オペレータ シーン出力
class MYADDON_OT_export_scene(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"

    def execute(self, context):

        print("シーン情報をExportします")

        # シーン内の全オブジェクトについて
        for object in bpy.context.scene.objects:
            print(object.type + "-" + object.name)
            #ローカルトランスフォーム行列から平行移動、回転、スケーリング
            trans, rot, scale = object.matrix_local.decompose()
            # 回転を クォータニオンからオイラーに変換
            rot = rot.to_euler()
            #　ラジアンから度数法に変換
            rot.x = math.degrees(rot.x)
            rot.y = math.degrees(rot.y)
            rot.z = math.degrees(rot.z)
            print("Trans(%f,%f,%f)" % (trans.x, trans.y, trans.z ))
            print("ROT(%f,%f,%f)" % (rot.x, rot.y, rot.z ))
            print("Scale(%f,%f,%f)" % (scale.x, scale.y, scale.z ))
            if object.parent:
                print("Parent" + object.name)
            print()


        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")

        return {'FINISHED'}
    

# トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    # blenderがクラスを識別するための文字列
    bl_idname = "TOPBAR_MT_my_menu"
    # メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    # 著者表示用の文字列
    bl_description = "拡張メニュー by " + bl_info["author"]

    # サブメニューの描画
    def draw(self, context):

        #トップバーのエディタメニューに項目（オペレーター）を追加
        self.layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        self.layout.separator()
        self.layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        self.layout.separator()
        self.layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)

    # 既存のメニューにサブメニューを追加
    def submenu(self, context):

        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)



# Blenderに登録するクラスリスト
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
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
    print("LevelEditor Enabled")
    
# AddonDisabledCallback
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    # blenderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("LevelEditor Disabled")
    
    
# testCode
if __name__ == "__main__":
    register()
 