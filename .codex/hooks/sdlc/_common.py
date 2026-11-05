"""hooks 共通処理。終了コード 2 + stderr でツール呼び出しを拒否する（Codex に理由が返る）。

この hooks は ~/.codex/hooks/sdlc/（全プロジェクト共通）にも、プロジェクトの .codex/hooks/sdlc/ にも置ける。
  - プロジェクトに .codex/hooks/sdlc/ があれば、~/.codex 側の hook は何もしない（プロジェクト版が上書き）
  - ~/.codex 側の hook は、SDLC プロジェクト（project.yaml に workflow: sdlc）でだけ工程・TDD の検査をする
  - 本体ライブラリはプロジェクトの .codex/sdlc/lib を優先し、無ければ hook と同じ場所の .codex/sdlc/lib を使う
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # <base>/.codex/hooks/sdlc
BASE = HERE.parents[1]                           # <base>/.codex
def project_dir() -> Path:
    cwd = Path(os.environ.get("SDLC_HOOK_CWD") or os.getcwd()).resolve()
    return next((path for path in (cwd, *cwd.parents) if (path / ".git").exists()), cwd)


PROJECT_DIR = project_dir()
LOCAL_INSTALL = (PROJECT_DIR / ".codex").resolve() == BASE.resolve()


def _lib_dir() -> Path:
    project_lib = PROJECT_DIR / ".codex" / "sdlc" / "lib"
    return project_lib if (project_lib / "sdlc_lib").is_dir() else BASE / "sdlc" / "lib"


sys.path.insert(0, str(_lib_dir()))

# Windows でも Codex とのやり取り（JSON・メッセージ）を UTF-8 で行う
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def read_input() -> dict:
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except ValueError:
        return {}


def deny(msg: str):
    print(f"[SDLC ガード] {msg}", file=sys.stderr)
    sys.exit(2)


def allow():
    sys.exit(0)


def maintenance() -> bool:
    """人が SDLC_MAINTENANCE=1 で Codex を起動した場合のみワークフロー本体の編集を許可する。"""
    return os.environ.get("SDLC_MAINTENANCE") == "1"


def deferred() -> bool:
    """~/.codex 側の hook で、プロジェクトに自前の hooks がある（そちらに任せる）。"""
    name = Path(sys.argv[0]).name
    return not LOCAL_INSTALL and (PROJECT_DIR / ".codex" / "hooks" / "sdlc" / name).exists()


def sdlc_project(root) -> bool:
    """この hook が工程・TDD の検査をすべきプロジェクトか。"""
    from sdlc_lib.config import is_sdlc_project
    return (LOCAL_INSTALL and Path(root).resolve() == PROJECT_DIR) or is_sdlc_project(root)


def _probably_sdlc() -> bool:
    try:
        return sdlc_project(PROJECT_DIR)
    except Exception:  # noqa: BLE001
        return True


def run(fn):
    """ガード本体を実行する。SDLC プロジェクトでの内部エラーは安全側（拒否）に倒す。"""
    if deferred():
        allow()
    try:
        data = read_input()
        if not data:
            deny("hook 入力の JSON を読み取れません。")
        fn(data)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        if maintenance() or not _probably_sdlc():
            allow()
        deny(f"ガードの内部エラーのため拒否しました: {type(e).__name__}: {e}\n"
             "依存関係（pip install -r requirements.txt）と project.yaml を確認してください。")
