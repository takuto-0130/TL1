import bpy
import os
import bpy.ops

#オペレータ
class MYADDON_OT_spawn_symbol_import(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_spawn_symbol_import"
    bl_label = "出現ポイントシンボルインポート"
    bl_description = "出現ポイントのシンボルをインポートします"
    bl_options = {'REGISTER', 'UNDO'}
    prototype_object_name = "ProttypePlayerSpawn"
    object_name = "PlayerSpawn"


    def load_obj(self, symbol_type):

        # 重複ロード防止
        spawn_object = bpy.data.objects.get(SpawnNames.names[symbol_type][SpawnNames.PROTOTYPE])
        if spawn_object is not None:
            return {'CANCELLED'}

        # スクリプトが配置されているディレクトリの名前を取得する
        addon_directory = os.path.dirname(__file__)
        # ディレクトリからのモデルファイルの相対パスを記述
        relative_path = SpawnNames.names[symbol_type][SpawnNames.FILENAME]
        # 合成してモデルファイルのフルパスを得る
        full_path = os.path.join(addon_directory, relative_path)

        # オブジェクトをインポート
        bpy.ops.wm.obj_import(
            'EXEC_DEFAULT',
            filepath=full_path,
            display_type='THUMBNAIL',
            forward_axis='Z', up_axis='Y'
        )
        # 回転を適用
        bpy.ops.object.transform_apply(
            location=False,
            rotation=True,
            scale=False,
            properties=False,
            isolate_users=False
        )

        # アクティブなオブジェクトを取得
        object = bpy.context.active_object
        # オブジェクト名を変更
        object.name = SpawnNames.names[symbol_type][SpawnNames.PROTOTYPE]

        # オブジェクトの種類を設定
        object["type"] = SpawnNames.names[symbol_type][SpawnNames.INSTANCE]

        # メモリ上に置いておくがシーンから外す
        bpy.context.collection.objects.unlink(object)


        return {'FINISHED'}


    def execute(self, context):
        print("出現ポイントのシンボルをインポートします")
        # Enemy読み込み
        self.load_obj("Enemy")
        # Player読み込み
        self.load_obj("Player")

        return {'FINISHED'}


    

#オペレータ 出現ポイントのシンボルを作成・配置する
class MYADDON_OT_spawn_symbol_create(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_spawn_symbol_create"
    bl_label = "出現ポイントシンボル作成"
    bl_description = "出現ポイントのシンボルを作成します"
    bl_options = {'REGISTER', 'UNDO'}

    # プロパティ
    symbol_type: bpy.props.StringProperty(name="Type", default="Player")
    
    def execute(self, context):
        # 読み込み済みのコピー元オブジェクトを検索
        spawn_object = bpy.data.objects.get(SpawnNames.names[self.symbol_type][SpawnNames.PROTOTYPE])

        # まだ読み込んでいない場合
        if spawn_object is None:
            # 読み込みオペレータを実行
            bpy.ops.myaddon.myaddon_spawn_symbol_import('EXEC_DEFAULT')
            # 再建策
            spawn_object = bpy.data.objects.get(SpawnNames.names[self.symbol_type][SpawnNames.PROTOTYPE])
            
        print("出現ポイントのシンボルを作成します")

        # Blenderでの選択を解除する
        bpy.ops.object.select_all(action='DESELECT')

        # 複製元の非表示オブジェクトを複製する
        object = spawn_object.copy()

        # 複製したオブジェクトを現在のシーンにリンク
        bpy.context.collection.objects.link(object)

         # オブジェクト名を変更
        object.name = SpawnNames.names[self.symbol_type][SpawnNames.INSTANCE]

        return {'FINISHED'}
    
class SpawnNames():

    # インデックス
    PROTOTYPE = 0 # プロトタイプのオブジェクト名
    INSTANCE = 1 # 量産時のオブジェクト名
    FILENAME = 2 # リソースファイル名

    names = {}
    # names["キー"] = (プロトタイプのオブジェクト名、量産時のオブジェクト名、リソースファイル名)
    names["Enemy"] = ("PrototypeEnemySpawn", "EnemySpawn", "EnemyBody/EnemyBody.obj")
    names["Player"] = ("PrototypePlayerSpawn", "PlayerSpawn", "cube/cube.obj")

class MYADDON_OT_spawn_symbol_player(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_spawn_symbol_player"
    bl_label = "プレイヤー出現ポイントシンボル作成"
    bl_description = "プレイヤー出現ポイントのシンボルを作成します"

    def execute(self, context):
        
        bpy.ops.myaddon.myaddon_spawn_symbol_create('EXEC_DEFAULT', symbol_type = "Player")

        return {'FINISHED'}

class MYADDON_OT_spawn_symbol_enemy(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_spawn_symbol_enemy"
    bl_label = "敵出現ポイントシンボル作成"
    bl_description = "敵出現ポイントのシンボルを作成します"

    def execute(self, context):
        
        bpy.ops.myaddon.myaddon_spawn_symbol_create('EXEC_DEFAULT', symbol_type = "Enemy")

        return {'FINISHED'}
