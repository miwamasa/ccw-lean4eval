from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import os
import tempfile
import anthropic
from typing import Optional

app = FastAPI()

# 静的ファイルのマウント
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("saved_files"):
    os.makedirs("saved_files")

app.mount("/static", StaticFiles(directory="static"), name="static")


class CodeExecutionRequest(BaseModel):
    code: str


class FileSaveRequest(BaseModel):
    filename: str
    code: str


class FileLoadRequest(BaseModel):
    filename: str


class ChatRequest(BaseModel):
    message: str
    code: str
    context: Optional[str] = None


@app.get("/")
async def read_root():
    return FileResponse("index.html")


@app.post("/api/execute")
async def execute_lean_code(request: CodeExecutionRequest):
    """Lean4コードを実行してエラーや結果を返す"""
    try:
        # 一時ファイルを作成してLean4コードを保存
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as temp_file:
            temp_file.write(request.code)
            temp_file_path = temp_file.name

        try:
            # Lean4でコードをチェック
            result = subprocess.run(
                ['lean', temp_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr

            return JSONResponse({
                "success": result.returncode == 0,
                "output": output,
                "errors": result.stderr if result.returncode != 0 else ""
            })
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except subprocess.TimeoutExpired:
        return JSONResponse({
            "success": False,
            "output": "",
            "errors": "実行がタイムアウトしました（30秒）"
        })
    except FileNotFoundError:
        return JSONResponse({
            "success": False,
            "output": "",
            "errors": "Lean4がインストールされていません。インストール手順については README.md を参照してください。"
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "output": "",
            "errors": f"実行エラー: {str(e)}"
        })


@app.post("/api/save")
async def save_file(request: FileSaveRequest):
    """Lean4ファイルを保存"""
    try:
        filepath = os.path.join("saved_files", request.filename)

        # ファイル名のセキュリティチェック
        if ".." in request.filename or "/" in request.filename:
            raise HTTPException(status_code=400, detail="無効なファイル名です")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(request.code)

        return JSONResponse({
            "success": True,
            "message": f"ファイル '{request.filename}' を保存しました"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存エラー: {str(e)}")


@app.post("/api/load")
async def load_file(request: FileLoadRequest):
    """Lean4ファイルを読み込み"""
    try:
        filepath = os.path.join("saved_files", request.filename)

        # ファイル名のセキュリティチェック
        if ".." in request.filename or "/" in request.filename:
            raise HTTPException(status_code=400, detail="無効なファイル名です")

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")

        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        return JSONResponse({
            "success": True,
            "code": code
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"読み込みエラー: {str(e)}")


@app.get("/api/files")
async def list_files():
    """保存されたファイルの一覧を取得"""
    try:
        files = [f for f in os.listdir("saved_files") if f.endswith('.lean')]
        return JSONResponse({
            "success": True,
            "files": files
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "files": [],
            "error": str(e)
        })


@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """AIチャット機能 - コードについての質問に回答"""
    try:
        # 環境変数からAPIキーを取得
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return JSONResponse({
                "success": False,
                "response": "エラー: ANTHROPIC_API_KEY環境変数が設定されていません"
            })

        client = anthropic.Anthropic(api_key=api_key)

        # コンテキストを含むプロンプトを作成
        system_prompt = """あなたはLean4の証明支援エキスパートです。
ユーザーのLean4コードに関する質問に、わかりやすく日本語で回答してください。
コードのエラー、証明の進め方、型の問題などについてアドバイスを提供してください。"""

        user_message = f"""以下のLean4コードについて質問があります：

```lean
{request.code}
```

質問: {request.message}
"""

        if request.context:
            user_message += f"\n\n追加のコンテキスト: {request.context}"

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        response_text = message.content[0].text

        return JSONResponse({
            "success": True,
            "response": response_text
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "response": f"AIチャットエラー: {str(e)}"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
