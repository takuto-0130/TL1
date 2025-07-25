#include "BlenderLevelLoader.h"
#include <fstream>
#include <numbers>

#include "LevelObject.h"

using json = nlohmann::json;

LevelData* BlenderLevelLoader::Load(const std::string& filename)
{
    std::ifstream file(kBaseDirectoryName_ + filename);
    if (!file.is_open()) assert(0);

    json j;
    file >> j;

    // 正しいレベルデータファイルかをチェックする
    assert(j.is_object());
    assert(j.contains("name"));
    assert(j["name"].is_string());
    std::string name = j["name"].get<std::string>();
    assert(name.compare("scene") == 0);

    // レベルデータ格納用インスタンスの生成
    LevelData* levelData = new LevelData();

    // "objects"の全オブジェクトを走査
    ObjectTraversal(levelData, j, "objects");

    return levelData;
}

void BlenderLevelLoader::DataToObject(LevelData* data, std::vector<std::unique_ptr<LevelObject>>& objects)
{
    for (auto& objectData : data->objects)
    {
        std::string modelName = objectData.fileName + ".obj";
        std::unique_ptr<LevelObject> object = std::make_unique<LevelObject>();
        object->SetModelName(modelName);
        object->Init();
        object->SetPosition(objectData.translation);
        Vector3 rotation = {
            objectData.rotation.x * (std::numbers::pi_v<float> / 180.0f),
            objectData.rotation.y * (std::numbers::pi_v<float> / 180.0f) * (-1.0f),
            objectData.rotation.z * (std::numbers::pi_v<float> / 180.0f),
        };
        object->SetRotation(rotation);
        object->SetScale(objectData.scaling);
        objects.push_back(std::move(object));
    }
}

void BlenderLevelLoader::ObjectTraversal(LevelData* levelData, json& j, std::string contains)
{
    for (json& object : j[contains])
    {
        assert(object.contains("type"));

        // 無効化フラグが有効ならスキップ
        if (object.contains("disable_flag"))
        {
            bool disabled = object["disable_flag"].get<bool>();
            if (disabled)
            {
                continue;
            }
        }

        // 種類を取得
        std::string type = object["type"].get<std::string>();

        if (type.compare("MESH") == 0)
        {
            // 要素追加
            levelData->objects.emplace_back(LevelData::ObjectData{});
            // 追加した要素の参照を得る
            LevelData::ObjectData& objectData = levelData->objects.back();

            if (object.contains("file_name"))
            {
                objectData.fileName = object["file_name"];
            }

            json& transform = object["transform"];
            // 平行移動
            if (transform.contains("translation") && transform["translation"].size() >= 3)
            {
                objectData.translation.x = static_cast<float>(transform["translation"][0]);
                objectData.translation.y = static_cast<float>(transform["translation"][2]);
                objectData.translation.z = static_cast<float>(transform["translation"][1]);
            }

            // 回転角
            if (transform.contains("rotation") && transform["rotation"].size() >= 3)
            {
                objectData.rotation.x = static_cast<float>(transform["rotation"][0]);
                objectData.rotation.y = static_cast<float>(transform["rotation"][2]);
                objectData.rotation.z = static_cast<float>(transform["rotation"][1]);
            }

            // スケーリング
            if (transform.contains("scaling") && transform["scaling"].size() >= 3)
            {
                objectData.scaling.x = static_cast<float>(transform["scaling"][0]);
                objectData.scaling.y = static_cast<float>(transform["scaling"][2]);
                objectData.scaling.z = static_cast<float>(transform["scaling"][1]);
            }

            // 再帰的に枝を走査する
            if (object.contains("children"))
            {
                //levelData->objects.reserve(LevelData);
                ObjectTraversal(levelData, object, "children");
            }
        }
        else if (type.compare("PlayerSpawn") == 0)
        {
            // 要素追加
            levelData->players.emplace_back(LevelData::PlayerSpawnData{});
            // 追加した要素の参照を得る
            LevelData::PlayerSpawnData& data = levelData->players.back();

            json& transform = object["transform"];
            // 平行移動
            if (transform.contains("translation") && transform["translation"].size() >= 3)
            {
                data.translation.x = static_cast<float>(transform["translation"][0]);
                data.translation.y = static_cast<float>(transform["translation"][2]);
                data.translation.z = static_cast<float>(transform["translation"][1]);
            }

            // 回転角
            if (transform.contains("rotation") && transform["rotation"].size() >= 3)
            {
                data.rotation.x = static_cast<float>(transform["rotation"][0]);
                data.rotation.y = static_cast<float>(transform["rotation"][2]);
                data.rotation.z = static_cast<float>(transform["rotation"][1]);
            }
        }
        else if (type.compare("EnemySpawn") == 0)
        {
            // 要素追加
            levelData->enemies.emplace_back(LevelData::EnemySpawnData{});
            // 追加した要素の参照を得る
            LevelData::EnemySpawnData& data = levelData->enemies.back();

            if (object.contains("file_name"))
            {
                data.fileName = object["file_name"];
            }

            json& transform = object["transform"];
            // 平行移動
            if (transform.contains("translation") && transform["translation"].size() >= 3)
            {
                data.translation.x = static_cast<float>(transform["translation"][0]);
                data.translation.y = static_cast<float>(transform["translation"][2]);
                data.translation.z = static_cast<float>(transform["translation"][1]);
            }

            // 回転角
            if (transform.contains("rotation") && transform["rotation"].size() >= 3)
            {
                data.rotation.x = static_cast<float>(transform["rotation"][0]);
                data.rotation.y = static_cast<float>(transform["rotation"][2]);
                data.rotation.z = static_cast<float>(transform["rotation"][1]);
            }
        }
    }
}
