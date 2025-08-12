# MLGame
![mlgame](https://img.shields.io/github/v/tag/PAIA-Playful-AI-Arena/mlgame)
![mlgame](https://img.shields.io/pypi/v/mlgame)
  
[![Python 3.10](https://img.shields.io/badge/python->3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
[![pygame](https://img.shields.io/badge/pygame->2.5.2-blue.svg)](https://github.com/pygame/pygame/releases/tag/2.5.2)

---
這是一個遊戲ＡＩ競賽的框架，依照此框架所開發的遊戲，可以透過ＡＩ來玩遊戲，並進行ＡＩ競賽。


# 使用方式

## 終端機範例
- 列出 help 文件
  ```shell
  python -m mlgame -h
  ```

- 命令列格式
    ```shell
    python -m mlgame [options] <game_folder> [game_params]
    ```
  - 執行打磚塊遊戲
    ```shell
    python -m mlgame \
    -f 120 -i ./path/to/ai/ai_client_file_name.py \
    ./path/to/game/arkanoid \
    --difficulty NORMAL --level 3
    ```
    - AI和遊戲的資料夾路徑可以使用`相對路徑`或是`絕對路徑` 
    - 遊戲參數`game_params`須參考各個遊戲 

## 位置引數(Positional Argument)
- `game_folder`
  - `required` 
  - 遊戲資料夾所在的路徑，此路徑下需有`config.py`


## 功能性引數(Functional Argument) 
### `options`
- `--version` 顯示MLGame版本號
- `-h`, `--help`
  - 提供參數的說明
- `-f` `FPS`, `--fps` `FPS`
  - 設定遊戲的遊戲更新率(frame per second)，遊戲預設為每秒更新30次。
  - `default` : `30`
- `-1`, `--one-shot`
  - 表示遊戲只執行一次，沒有加上這個參數，遊戲皆會不斷重新執行。 
  - `default` : `False`
- `--nd`, `--no-display`
  - 加上此參數就不會顯示螢幕畫面。 
  - `default` : `False`
- `--ws_url` `WS_URL`
  - 加上此參數，會建立一個websocket connection，並將遊戲過程中的資料傳到指定的路徑，若路徑失效，則遊戲無法啟動。
- `-i` `AI_Client`, `--input-ai` `AI_Client`
  - 指定要玩遊戲的AI，AI的檔案中，需要包含`MLPlay`這個class。
  - 若有多個玩家，可直接參考下方案例，路徑可以使用絕對路徑與相對路徑。
    ```
    -i ./path/to/ai/ai_01.py -i ./path/to/ai/ai_02.py 
    ```
  - AI數量需符合遊戲需求，每個遊戲都會有最小值與最大值，不足的會以最後一個AI自動補足，多的會自動刪去。
    - 遊戲若需要2個AI，給到1個AI則會同時扮演1P 2P
    - 遊戲若需要2個AI，給到3個AI則會自動排除最後一個
- `-o` `output_folder`, `--output-folder` `output_folder`
  - 將遊戲過程儲存到特定資料夾中，會自動建立一個時間戳記資料夾來儲存每一幀的圖片。
  - 此資料夾需要可讀寫，並且為有效路徑。
  - 若是沒有加上 `-1` ，會不斷的紀錄遊戲結果。
  - 此選項會影響到執行效能，開啟後覺得卡頓屬於正常現象。
- `-r` `progress-folder`, `--progress-folder` `progress-folder`
  - 將遊戲每個 frame 儲存到特定資料夾中，會自動建立一個時間戳記資料夾來儲存各 frame 的內容，以檔案分開。
  - 可透過 `-p`, `--progress-frame-frequency` 指定一個檔案內的 frame 數量。
  - 檔案內容為 json，檔案名稱代表此檔案由哪個 frame 開始紀錄。
  - 此資料夾需要可讀寫，並且為有效路徑。
- `-p` `progress-frame-frequency`, `--progress-frame-frequency` `progress-frame-frequency`
  - 與 `-r`, `--progress-folder` 搭配。
  - 可指定一個檔案內的 frame 數量。
- `--ns` , `--no-sound`
  - 預設會開啟音效設定，加上此參數會關閉音效。

- `--debug`  
  - 顯示debug 資訊，並紀錄`debug.log`檔案

[//]: # (-  `--group_ai` `GROUP_AI_ORIG`)

[//]: # (  - 格式：--group_ai `隊伍編號`,`玩家編號`,`AI路徑`,`AI名稱`)

[//]: # (    - ex: --group_ai A,1P,/path/to/ml_play.py,ai_label)

[//]: # (  - 設定有組隊的AI，隊伍編號應為 ['A','B','C','D'] 之一，玩家編號應為 ['1P','2P',...,'8P']。)

[//]: # (  - 注意：此參數將覆蓋 --input-ai 或 -i 的輸入。)

[//]: # (  )
- `--az_upload_url` `AZ_UPLOAD_URL`  
  - 將遊戲過程紀錄檔案上傳至azure blob, `AZ_UPLOAD_URL`需包含連結字串
  


### `game_params`
- `optional` 
- 執行遊戲的參數依照每個遊戲有所不同，格式為`--name_of_params` `value_of_params`
- type 
  - int : `0` `1` `-1` `1.5` 
  - str : `"0"` `"hello"` `"NORMAL"`
  - list: `0,1` `-1,1000,111` `abc,cde,12` 
  - path: `./relative_path_to_file/file.txt`,`/absoulute_path_to_file/file.dat` 

# 畫面控制
- 遊戲執行可以使用 `I` `J` `K` `L` 進行平移
- 使用 `U` `O`放大縮小
- 使用 `H` 開啟或關閉部分資訊
- 使用 `P` 暫停遊戲畫面，暫停期間，遊戲邏輯不會運作，但仍可以調整畫面。
- 使用 `M` 在遊戲過程中開關音樂與音效。


[//]: # (# 其他)

[//]: # ()
[//]: # (1. [系統架構]&#40;./docs/System.md&#41;)


   
# 相關專案

> 1. [PAIA-Desktop](https://github.com/PAIA-Playful-AI-Arena/Paia-Desktop)
> 2. 範例遊戲 [easy_game](https://github.com/PAIA-Playful-AI-Arena/easy_game)
> 3. 打磚塊 [arkanoid](https://github.com/PAIA-Playful-AI-Arena/arkanoid)
> 4. 乒乓球 [pingpong](https://github.com/PAIA-Playful-AI-Arena/pingpong)
> 5. 賽車 [Racing Car](https://github.com/PAIA-Playful-AI-Arena/racing_car)
> 6. 迷宮自走車 [Maze Car](https://github.com/PAIA-Playful-AI-Arena/maze_car)

# Future Work

1. [ ] Non-python Client Support
2. [ ] test case
4. [ ] 遊戲開發文件
5. [ ] 

## Change Log

View [CHANGELOG.md](./CHANGELOG.md)

# 開發與測試

## 環境變數設定

MLGame 框架支援使用環境變數來設定開發和測試時的路徑，避免硬編碼敏感資訊。所有環境變數都定義在 `mlgame/tests/env.py` 中。

### 可用的環境變數

- `MLGAME_BASE_PATH`: MLGame 專案的基礎路徑
- `MLGAME_GAMES_PATH`: 遊戲目錄的路徑
- `MLGAME_AI_CLIENTS_PATH`: AI 客戶端目錄的路徑
- `MLGAME_OUTPUT_PATH`: 輸出目錄的路徑
- `MLGAME_VERBOSE_TESTS`: 啟用測試時的詳細路徑記錄
- `MLGAME_AZURE_CONTAINER_URL`: azure blob container 路徑
- `MLGAME_AZURE_BLOB_URL`: azure blob 路徑


### 使用 .env 檔案

您可以在測試資料夾中建立 `.env` 檔案來設定環境變數。專案中提供了 `.env.sample` 作為範例。

```
# .env 檔案範例
MLGAME_BASE_PATH=/path/to/your/mlgame
```

要使用 .env 檔案，需安裝 python-dotenv 套件：

```bash
pip install python-dotenv
```

### 在程式中使用環境變數

要在您的程式中使用這些環境變數，只需從 env 模組匯入它們：

```python
from mlgame.tests.env import BASE_PATH, GAMES_PATH, AI_CLIENTS_PATH, get_path

# 使用環境變數生成路徑
game_path = get_path(GAMES_PATH, 'my_game')
```
