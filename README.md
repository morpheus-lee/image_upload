# Superset 圖片管理

支援 Apache Superset 6.1.0。從主選單開啟「圖片管理」即可上傳圖片，並依上傳順序由新到舊查看縮圖、檔名和台北時間。列表每頁 20 筆，點選檔名可開啟原圖。

## 安裝

1. 將 `image-library-0.1.0.supx` 放入 Superset 的 Extension 目錄。
2. 在既有的 `superset_config.py` 合併下列設定。把 SQLite 資料庫所在目錄掛載到持久化磁碟，並給 Superset 程序寫入權限。若省略 `IMAGE_LIBRARY_DB_PATH`，預設使用 Superset 的 `DATA_DIR/image-library/images.sqlite3`。

   ```python
   FEATURE_FLAGS = {
       # 保留其他既有的 feature flags。
       "ENABLE_EXTENSIONS": True,
   }
   EXTENSIONS_PATH = "/app/extensions"
   IMAGE_LIBRARY_DB_PATH = "/app/image-data/images.sqlite3"
   ```

3. 確認 Superset Python 環境中的 Pillow 支援 JPEG、PNG、WebP。可用 `python -m PIL` 查詢。
4. 在同一組設定下執行 `superset init`，再重啟 Superset。
5. 在 **Settings → List Roles** 為角色授權。

| 用途 | 權限 |
| --- | --- |
| 顯示選單及檢視列表、縮圖與原圖 | `menu access on 圖片管理` 和 `can read on ImageLibrary` |
| 上傳 | 上述權限加上 `can write on ImageLibrary` |

## 檔案與資料

- 每次可上傳一張靜態 JPEG、PNG 或 WebP，最多 10 MiB 且最多 2,000 萬像素。伺服器會解碼驗證並產生縮圖。
- 反向代理可對 `/extensions/local/image-library/upload` 設定 11 MiB 的請求上限，以涵蓋表單開銷。
- 原圖、縮圖與中繼資料存於同一個 SQLite 資料庫，適用於單台 Superset 主機及其本機 workers。有讀取權限的使用者共用同一份圖片庫。請備份資料庫。

## 重新打包

在專案目錄執行：

```sh
python -m pip install apache-superset-extensions-cli==0.1.0
superset-extensions bundle
```
