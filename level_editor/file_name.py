import bpy

# モジュールのインポート
from .add_file_name import MYADDON_OT_add_filename
    
# パネル ファイル名
class OBJECT_PT_file_name(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    # サブメニューの描画
    def draw(self, context):

        # パネルに項目を追加
        if "file_name" in context.object:
            # プロパティがあれば表示
            self.layout.prop(context.object, '["file_name"]', text=self.bl_label)
        else:
            # プロパティがなければプロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_filename.bl_idname)