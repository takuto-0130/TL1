import bpy, json, gpu, os
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty

bl_info = {
    "name": "Stage Data Editor",
    "blender": (3, 0, 0),
    "category": "Object",
}

handler = None

# ==================== Catmull-Rom 曲線 ====================

def catmull_rom(p0, p1, p2, p3, t):
    s = 0.5
    t2 = t * t
    t3 = t2 * t
    e3 = -p0 + 3*p1 - 3*p2 + p3
    e2 = 2*p0 - 5*p1 + 4*p2 - p3
    e1 = -p0 + p2
    e0 = 2*p1
    return s * (e3 * t3 + e2 * t2 + e1 * t + e0)

def catmull_rom_position(points, t):
    division = len(points) - 1
    area_width = 1.0 / division
    t2 = (t % area_width) * division
    t2 = max(0.0, min(1.0, t2))
    index = int(t / area_width)
    index = min(index, division - 1)
    i0 = max(index-1, 0)
    i1 = index
    i2 = index+1
    i3 = min(index+2, len(points)-1)
    return catmull_rom(points[i0], points[i1], points[i2], points[i3], t2)

def draw_curve():
    empties = [obj for obj in bpy.data.objects if obj.type == "EMPTY"]
    if len(empties) < 4:
        return

    points = [obj.location for obj in empties]
    verts = [catmull_rom_position(points, i / 99.0) for i in range(100)]

    # Blender 4.0+は POLYLINE_UNIFORM_COLOR を使う
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": verts})

    shader.bind()
    shader.uniform_float("color", (1.0, 1.0, 0.0, 1.0))
    shader.uniform_float("lineWidth", 2.0)  # 線の太さ設定
    batch.draw(shader)

def enable_draw():
    global handler
    print("enable_draw called")  # デバッグ
    if handler is None:
        print("draw_handler_add 登録")  # デバッグ
        handler = bpy.types.SpaceView3D.draw_handler_add(draw_curve, (), 'WINDOW', 'POST_VIEW')

def disable_draw():
    global handler
    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        handler = None


# ==================== データ入出力 ====================

def export_stage_data(filepath):
    stage_data = {"enemy": {"groups": []}, "rail": {"controlPoints": []}}

    # 敵グループ
    for col in bpy.data.collections:
        group = []
        for obj in col.objects:
            if obj.type == "MESH":
                loc = obj.location
                group.append({
                    "x": loc.x,
                    "y": loc.z,   # Blender Z → ゲーム Y
                    "z": loc.y    # Blender Y → ゲーム Z
                })
        if group:
            stage_data["enemy"]["groups"].append(group)

    # rail（Empty）
    empties = [obj for obj in bpy.data.objects if obj.type == "EMPTY"]
    empties.sort(key=lambda e: e.name)
    for e in empties:
        loc = e.location
        trigger = e.get("triggerEvent", False)  # カスタムプロパティ取得
        stage_data["rail"]["controlPoints"].append({
            "x": loc.x,
            "y": loc.z,
            "z": loc.y,
            "segmentSpeed": 1.0,
            "triggerEvent": trigger
        })

    with open(filepath, "w") as f:
        json.dump(stage_data, f, indent=4)


def import_stage_data(filepath):
    if not os.path.exists(filepath):
        print("stage_data.jsonが見つかりません")
        return

    with open(filepath, "r") as f:
        stage_data = json.load(f)

    # 既存オブジェクトを削除
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # 敵グループを再構築
    for i, group in enumerate(stage_data["enemy"]["groups"]):
        col_name = f"Group{i+1}"
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

        for enemy in group:
            # ゲーム座標系 → Blender座標系に変換
            pos = (enemy["x"], enemy["z"], enemy["y"])  # YとZを入れ替え
            bpy.ops.mesh.primitive_uv_sphere_add(location=pos)
            obj = bpy.context.active_object
            obj.scale = (0.3, 0.3, 0.3)

            if obj.name not in col.objects:
                col.objects.link(obj)
            if obj.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(obj)

    # rail 制御点
    for cp in stage_data["rail"]["controlPoints"]:
        pos = (cp["x"], cp["z"], cp["y"])
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos)
        empty = bpy.context.active_object
        empty["triggerEvent"] = cp.get("triggerEvent", False)


# ==================== UIの操作クラス ====================

class OBJECT_OT_add_enemy(bpy.types.Operator):
    bl_idname = "object.add_enemy"
    bl_label = "敵を追加"
    
    def execute(self, context):
        col = context.collection
        bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.scale = (0.3, 0.3, 0.3)
        col.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)  # デフォルトコレクションから外す
        return {'FINISHED'}

class OBJECT_OT_add_rail(bpy.types.Operator):
    bl_idname = "object.add_rail"
    bl_label = "レール制御点を追加"

    def execute(self, context):
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
        return {'FINISHED'}

class OBJECT_OT_export_stage(bpy.types.Operator, ExportHelper):
    bl_idname = "object.export_stage"
    bl_label = "stage_data.json 出力"

    # 拡張子フィルタ
    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        export_stage_data(self.filepath)
        self.report({'INFO'}, f"{self.filepath} に書き出しました")
        return {'FINISHED'}

class OBJECT_OT_import_stage(bpy.types.Operator, ImportHelper):
    bl_idname = "object.import_stage"
    bl_label = "stage_data.json 読み込み"

    # デフォルトの拡張子フィルタ
    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        # self.filepath にユーザーが選択したパスが入る
        import_stage_data(self.filepath)
        self.report({'INFO'}, f"{self.filepath} を読み込みました")
        return {'FINISHED'}
    

class OBJECT_OT_toggle_curve(bpy.types.Operator):
    bl_idname = "object.toggle_curve"
    bl_label = "曲線表示 ON/OFF"

    def execute(self, context):
        if handler:
            print("disable_draw")  # デバッグ
            disable_draw()
        else:
            print("enable_draw")   # デバッグ
            enable_draw()
        return {'FINISHED'}

# ==================== パネル ====================

class OBJECT_PT_stage_panel(bpy.types.Panel):
    bl_label = "Stage Data Editor"
    bl_idname = "OBJECT_PT_stage_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'StageData'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.add_enemy")
        layout.operator("object.add_rail")
        layout.operator("object.toggle_curve")
        layout.operator("object.export_stage")
        layout.operator("object.import_stage")

        # Empty選択中なら triggerEvent プロパティを編集
        obj = context.active_object
        if obj and obj.type == "EMPTY":
            layout.prop(obj, '["triggerEvent"]', text="Trigger Event")
        

# ==================== 登録 ====================

classes = [
    OBJECT_OT_add_enemy,
    OBJECT_OT_add_rail,
    OBJECT_OT_export_stage,
    OBJECT_OT_import_stage,
    OBJECT_OT_toggle_curve,
    OBJECT_PT_stage_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    disable_draw()

if __name__ == "__main__":
    register()