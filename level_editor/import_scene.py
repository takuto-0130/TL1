import bpy
import json
import math
import mathutils
import bpy_extras
import os


class MYADDON_OT_import_scene(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "myaddon.myaddon_ot_import_scene"
    bl_label = "シーンインポート"
    bl_description = "シーン情報をImportします"
    filename_ext = ".json"

    # キャッシュ用辞書 {file_name: オブジェクト or Empty}
    import_cache = {}

    def get_models_dir(self):
        """このアドオンがあるフォルダ直下の models フォルダを返す"""
        addon_dir = os.path.dirname(__file__)
        models_dir = os.path.join(addon_dir, "models")
        return models_dir

    def duplicate_object(self, obj, parent=None):
        """オブジェクトを複製 (リンクではなく実体コピー)"""
        obj_copy = obj.copy()
        if obj.data:
            obj_copy.data = obj.data.copy()
        bpy.context.collection.objects.link(obj_copy)

        # 子も複製
        for child in obj.children:
            child_copy = self.duplicate_object(child, obj_copy)
            child_copy.parent = obj_copy

        if parent:
            obj_copy.parent = parent

        return obj_copy

    def load_external_model(self, file_name):
        # キャッシュがある場合は複製して返す
        if file_name in self.import_cache:
            return self.duplicate_object(self.import_cache[file_name])

        obj_path = os.path.join(self.get_models_dir(), file_name, file_name + ".obj")

        if not os.path.exists(obj_path):
            print(f"[WARN] {obj_path} が見つかりません")
            return None

        ext = os.path.splitext(obj_path)[1].lower()
        before_objs = set(bpy.data.objects)

        # Blender 4.x: wm.obj_import
        if ext == ".obj":
            bpy.ops.wm.obj_import(filepath=obj_path)
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=obj_path)
        elif ext in [".gltf", ".glb"]:
            bpy.ops.import_scene.gltf(filepath=obj_path)
        else:
            print(f"[WARN] 未対応の拡張子: {ext}")
            return None

        after_objs = set(bpy.data.objects)
        new_objs = list(after_objs - before_objs)

        if not new_objs:
            print(f"[ERROR] {file_name} のインポートに失敗しました")
            return None

        # キャッシュ登録と返却
        if len(new_objs) > 1:
            empty = bpy.data.objects.new(file_name, None)
            bpy.context.collection.objects.link(empty)
            for obj in new_objs:
                obj.parent = empty
            self.import_cache[file_name] = empty
            return empty    # 初回は複製しない
        else:
            self.import_cache[file_name] = new_objs[0]
            return new_objs[0]  # 初回は複製しない




    def create_object_from_json(self, json_obj, parent=None):
        """JSONオブジェクトからBlenderオブジェクトを作成"""

        obj_name = json_obj.get("name", "Object")
        file_name = json_obj.get("file_name", None)

        # file_nameがある場合 → 外部モデルをロード(キャッシュ利用)
        if file_name:
            obj = self.load_external_model(file_name)
            if not obj:
                obj = bpy.data.objects.new(obj_name, None)
                bpy.context.collection.objects.link(obj)
        else:
            obj = bpy.data.objects.new(obj_name, None)
            bpy.context.collection.objects.link(obj)

        # トランスフォーム設定
        transform = json_obj.get("transform", {})
        t = transform.get("translation", [0, 0, 0])
        r = transform.get("rotation", [0, 0, 0])
        s = transform.get("scaling", [1, 1, 1])

        obj.location = t
        # Blenderのrotation_modeを強制的に'XYZ'にする
        obj.rotation_mode = 'XYZ'

        # Euler(XYZ)を直接代入（逆変換なし）
        obj.rotation_euler = (
        math.radians(r[0] - 90.0),
        math.radians(r[1] - 180.0),
        math.radians(r[2])
)
        obj.scale = s

        # カスタムプロパティ
        if file_name:
            obj["file_name"] = file_name

        if "collider" in json_obj:
            collider = json_obj["collider"]
            obj["collider"] = collider.get("type", "")
            obj["collider_center"] = mathutils.Vector(collider.get("center", [0, 0, 0]))
            obj["collider_size"] = mathutils.Vector(collider.get("size", [1, 1, 1]))

        if "disable_flag" in json_obj:
            obj["disable_flag"] = json_obj["disable_flag"]

        # 親子付け
        if parent:
            obj.parent = parent

        # 子ノードがある場合は再帰
        for child_json in json_obj.get("children", []):
            self.create_object_from_json(child_json, obj)

        return obj

    def import_json(self):
        with open(self.filepath, "rt", encoding="utf-8") as file:
            data = json.load(file)

        objects = data.get("objects", [])
        for obj_data in objects:
            self.create_object_from_json(obj_data)

    def execute(self, context):
        print("シーン情報をImportします")
        self.import_cache.clear()  # キャッシュをリセット
        self.import_json()
        self.report({'INFO'}, "シーン情報をImportしました")
        print("シーン情報をImportしました")
        return {'FINISHED'}
