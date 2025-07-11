import bpy

#オペレータ カスタムプロパティ['disable_flag']追加
class MYADDON_OT_add_disable_flag(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_disable_flag"
    bl_label = "無効化フラグ 追加"
    bl_description = "['disable_flag']カスタムプロパティを追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # ['disable_flag']カスタムプロパティを追加
        context.object["disable_flag"] = True
        
        return {'FINISHED'}
    

#パネル 無効オプション
class OBJECT_PT_disable_flag(bpy.types.Panel):
    bl_idname = "OBJECT_PT_disable_flag"
    bl_label = "DisableFlag"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    # サブメニューの描画
    def draw(self, context):

        # パネルに項目を追加
        if "disable_flag" in context.object:
            # プロパティがあれば表示
            self.layout.prop(context.object, '["disable_flag"]', text="disable")
        else:
            # プロパティがなければプロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_disable_flag.bl_idname)

