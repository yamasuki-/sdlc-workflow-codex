# インストールと使い方

## 1. 準備

Git リポジトリ、Python 3.10 以上、Bash、hooks とサブエージェントが使える Codex CLI を用意します。Windows では Git for Windows の Bash を PATH に置きます。依存パッケージは、hooks とランチャが使う Python に入れます。必要に応じて `SDLC_PYTHON` を設定します。

このリポジトリのルートから、人の端末で実行します。

```bash
python -m pip install -r requirements.txt
python install.py --project /path/to/project
```

全プロジェクト共通にする場合は `python install.py --user` を使います。スキルは `.agents/skills/`、エージェントは `.codex/agents/`、hooks は `.codex/hooks.json`、本体は `.codex/sdlc/` に配置されます。ユーザー配置では既定のホーム配下を使います。両方に同名スキルを置くと Codex の選択画面に重複して表示される場合があります。プロジェクト側のスキルを選んでください。テンプレート等は `scripts/sdlc path <パス>` でプロジェクト版を優先して解決します。

`--dry-run` で変更を確認できます。同じコマンドで更新でき、`--uninstall` を付けて削除できます。配置後に編集した本体ファイルは既定で保存され、`--force` を指定した場合に置換・削除されます。

## 2. 初期化と実行

1. 対象リポジトリのルートで Codex を起動し、プロジェクトを信頼します。`/hooks` で SDLC の SessionStart と PreToolUse が登録・承認済みか確認します。
2. Codex に「`$sdlc-init` を使って初期化してください」と依頼します。言語、テストコマンド、ソースとテストの配置、機械チェックを確認して `project.yaml` を作ります。
3. `input/` に要求資料を置き、「`$sdlc` を使って進めてください」と依頼します。独立したサブエージェントによるレビューを含み、工程ゲートで停止します。
4. `docs/<工程>/review.md`、`checks.md`、成果物を人が確認し、Codex の外の対話端末で `scripts/approve 00` のように承認・条件付き承認・差戻しを記録します。Windows の PowerShell / コマンドプロンプトでは `scripts\approve.cmd 00` を使います。
5. 承認記録を人がコミットし、Codex で `$sdlc` を再実行します。中断からの再開も同じ手順です。

Codex は `AGENTS.md` の指示に従い、`scripts/sdlc path RULES.md` で全体ルールを解決します。既存プロジェクトの指示には初期化時に参照行を追記します。

## 3. 日常操作

| 操作 | コマンド |
|---|---|
| 現在工程と承認状態 | `scripts/sdlc status` |
| 本体と上書きの確認 | `scripts/sdlc where` |
| 工程の成果物一覧 | `scripts/sdlc gate artifacts <工程>` |
| 機械チェック | `scripts/sdlc check` |
| トレーサビリティ | `scripts/sdlc trace check` / `scripts/sdlc trace matrix` |
| Red / Green の証跡 | `scripts/sdlc test-run --expect red` / `scripts/sdlc test-run --expect green` |
| 未解決事項 | `scripts/sdlc question list` |

工程別の規則は `rules/common.md`、`rules/<工程ID>.md`、レビュー観点は `rules/review-<工程ID>.md` に置きます。機械チェックは `project.yaml` の `checks` に MUST / SHOULD / MAY で定義します。

不具合は `$defect`、変更要求は `$change` で起票します。調査と提案を確認して、外部端末で `scripts/approve defect DEF-xxx` または `scripts/approve change CR-xxx` を実行します。

## 4. ガードと適用範囲

- Codex の `apply_patch` に対し、追加・更新・削除・移動の全パスを検査します。前工程の有効な承認、承認済み成果物の凍結、ソース編集前の Red を確認します。承認時は成果物の SHA-256 と MUST チェックを使います。
- シェルの編集・承認呼び出しの検出はヒューリスティックです。hook の無効化・未承認、hook 起動自体の失敗、監視対象外のツールがある場合には強制できません。承認記録の保護には人による差分確認とリポジトリ側のアクセス制御も必要です。
- 工程スキルは冒頭で前工程の状態を確認します。Codex のスキル選択自体はブロックせず、工程成果物の編集を hook でガードします。
- タスクは最大 2 件を委譲します。サブエージェントへ作業ツリーを割り当てられない場合はメイン作業ツリーで逐次実行します。独立レビューを行うサブエージェントが利用できない環境では工程を停止します。
- 本体を保守するときは、人が `SDLC_MAINTENANCE=1` を付けて Codex を起動します。このモードでも `state/gates/` は手動承認で管理します。
- テストはソースと別のディレクトリに置きます。テストをソースと同じディレクトリに置く構成は対象外です。

Codex の設定仕様は [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[スキル](https://learn.chatgpt.com/docs/build-skills)、[hooks](https://learn.chatgpt.com/docs/hooks)、[サブエージェント](https://learn.chatgpt.com/docs/agent-configuration/subagents) を参照してください。
