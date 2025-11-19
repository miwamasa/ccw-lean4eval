# Lean4 証明補助ワークベンチ

Lean4を使った証明を補助するWebベースのワークベンチです。

## 機能

- ✅ **Lean4エディタ**: シンタックスハイライト付きコードエディタ
- ✅ **シンタクスチェック**: リアルタイムでLean4コードをチェック
- ✅ **証明の実行**: Lean4コードを実行して結果を確認
- ✅ **エラー表示**: わかりやすいエラーメッセージ表示
- ✅ **AIチャット機能**: Claude APIを使用してコードについて質問
- ✅ **ファイル保存・読込**: Lean4ファイルの保存と読み込み

## セットアップ

### 1. Lean4のインストール

```bash
# elanのインストール（Lean4のバージョン管理ツール）
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# パスを通す
source ~/.profile

# Lean4のインストール確認
lean --version
```

### 2. Pythonの依存関係をインストール

```bash
# Python 3.8以上が必要です
pip install -r requirements.txt
```

### 3. Anthropic API キーの設定

AIチャット機能を使用するには、Anthropic APIキーが必要です。

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

または、`.env`ファイルを作成して設定することもできます。

## 使い方

### サーバーの起動

```bash
python app.py
```

サーバーが起動したら、ブラウザで `http://localhost:8000` にアクセスしてください。

### ワークベンチの使い方

1. **コードの編集**: 左側のエディタでLean4コードを編集
2. **実行**: 「▶ 実行」ボタンをクリックしてコードを実行
3. **シンタクスチェック**: 「✓ シンタクスチェック」ボタンでシンタックスをチェック
4. **ファイル保存**: ファイル名を入力して「💾 保存」ボタンで保存
5. **ファイル読込**: ドロップダウンからファイルを選択して読み込み
6. **AIチャット**: 右側のチャットパネルでコードについて質問

## プロジェクト構造

```
ccw-lean4eval/
├── app.py              # FastAPIバックエンド
├── index.html          # フロントエンドUI
├── requirements.txt    # Python依存関係
├── saved_files/        # 保存されたLean4ファイル（自動作成）
└── static/             # 静的ファイル（自動作成）
```

## API エンドポイント

- `POST /api/execute` - Lean4コードを実行
- `POST /api/save` - ファイルを保存
- `POST /api/load` - ファイルを読み込み
- `GET /api/files` - 保存されたファイルの一覧を取得
- `POST /api/chat` - AIチャット

## トラブルシューティング

### Lean4がインストールされていないエラー

```
Lean4がインストールされていません。インストール手順については README.md を参照してください。
```

上記のエラーが表示される場合は、Lean4をインストールしてください（セットアップの手順1を参照）。

### AIチャット機能が動作しない

```
エラー: ANTHROPIC_API_KEY環境変数が設定されていません
```

環境変数`ANTHROPIC_API_KEY`を設定してください。

## 開発

### 開発モードでサーバーを起動

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します！
