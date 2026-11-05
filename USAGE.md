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

## 5. 最初の1工程を試す

新規の検証用 Git リポジトリにプロジェクト配置でインストールし、`$sdlc-init` を実行します。初期化時に選ぶ言語・テストコマンドは対象プロジェクトのものです。ワークフロー本体の自己テストと区別してください。

1. このリポジトリの [サンプル要求](examples/sample-requirements.md) を、検証用リポジトリの `input/` にコピーします。
2. 検証用リポジトリで `scripts/sdlc project check` を実行し、設定を確認します。
3. Codex に「`$sdlc` を使って工程00を進めてください。人の承認が必要になったら止まってください」と依頼します。
4. `scripts/sdlc status` と `scripts/sdlc gate artifacts 00` で状態と対象ファイルを確認し、`docs/00-intake/` の成果物、`checks.md`、`review.md` を読みます。
5. 承認する場合は別の対話端末で `scripts/approve 00` を実行します。条件付き承認なら条件を記録し、差戻しなら修正すべき点を記録します。承認記録をコミットし、Codex に再度 `$sdlc` を依頼します。

`input/` の資料が取り込み対象です。元の文書を修正した場合は、承認済み成果物への影響を確認してください。承認済み工程を変更する場合は、変更要求または不具合対応を通します。

## 6. プロジェクト固有の設定

| 設定 | 用途 |
|---|---|
| `workflow: sdlc` | ユーザー配置のガードが SDLC プロジェクトを識別する印 |
| `language` / `test_framework` | タスク分解やテスト設計で参照する技術情報 |
| `src_dir` / `test_dir` / `test_dirs` | 工程ごとの編集対象とゲートの対象を決める |
| `commands.test` | 全テスト。終了コード 0 を成功とし、TDD ガードでも利用する |
| `commands.test_unit` など | 単体・結合・システムの個別実行。lint と coverage も指定可能 |
| `checks.common` / `checks.<工程ID>` | 全工程または指定工程の機械チェック。MUST・SHOULD・MAY を指定する |
| `parallel.max_tasks` | 同時に開始するタスク数の上限。既定は2 |

`src_dir` とテスト領域は分け、`docs/`・`input/`・`state/`・`scripts/`・`.codex/`・`.agents/` などの予約領域と重ならないようにします。工程別のテスト領域は既定で `<test_dir>/unit`、`integration`、`system`、`regression` です。

機械チェックには結果を判定するコマンドを登録します。自動修正を行うフラグは付けません。組み込みのトレーサビリティ検査に加え、プロジェクトに必要な検査を設定します。MUST の失敗が残っている間はレビューと承認に進めません。実行できなかったチェックはレポートの skipped を確認します。

要件や設計の不明点は `scripts/sdlc question list` で確認します。既定値、境界値、例外時の動作などが未決定なら、人が判断し、承認対象の要件・設計に反映します。チャットで回答した内容も、承認済み成果物を変更する場合は変更要求の手順に従います。

## 7. 配置・上書き・更新

- **ユーザー配置**は、複数リポジトリで本体を共有するときに使います。各リポジトリで `$sdlc-init` を実行します。
- **プロジェクト配置**は、チームで使う版をリポジトリに記録するときに使います。新しい環境でも Python 依存関係の導入と hooks の有効化を確認します。
- プロジェクト固有の規則はまず `rules/` に置きます。テンプレートを差し替える場合は、例えば `.codex/sdlc/templates/review.md` にプロジェクト版を置き、`scripts/sdlc path templates/review.md` で選択結果を確認します。

インストーラは**取得したワークフローのリポジトリ側**で実行します。既存プロジェクトを更新する前に、`--dry-run` で配置・更新・保持の対象を確認してください。

```bash
python install.py --project /path/to/project --dry-run
python install.py --project /path/to/project
python install.py --project /path/to/project --uninstall
```

ユーザー配置を管理する場合は `--project /path/to/project` の代わりに `--user` を指定します。設定変更後は Codex を起動し直し、hook の承認状態を確認します。

## 8. トラブルシュート

| 症状 | 確認すること |
|---|---|
| `$sdlc-init` が選べない | Codex を対象リポジトリで起動したか。プロジェクトの `.agents/skills/sdlc-init/SKILL.md` またはホームの同じパスに配置されたか |
| ランチャが見つからない | インストール後に対象リポジトリで `$sdlc-init` を実行したか |
| Python や依存が見つからない | `SDLC_PYTHON` の指定と、その Python への `requirements.txt` の導入を確認する |
| 編集ガードが動かない | Codex の `/hooks` で対象の PreToolUse が表示され、信頼・承認されているか。実行環境で Bash と Python が使えるか |
| 次工程に進まない | `scripts/sdlc status` と `scripts/sdlc gate status` を実行する。未承認、差戻し、成果物ハッシュの変化などの理由を確認する |
| 承認できない | 対話端末で実行しているか、前工程のゲートが有効か、MUST とレビューの結果が承認可能かを確認する |
| 実装コードを編集できない | 工程04の承認と、設定したテストコマンドで期待した失敗を再現できるかを確認する |
| 中断後に何をすべきか分からない | `scripts/sdlc status --json` で `next` を確認し、`$sdlc` を再実行する |

## 9. Windows でのコマンド例

PowerShell またはコマンドプロンプトからインストールする場合の例です。Git Bash はワークフローのシェルコマンドで使うため、`bash` が PATH にあることを確認します。

```powershell
py -3 -m pip install -r requirements.txt
py -3 install.py --project "C:\work\my-project"
Set-Location "C:\work\my-project"
codex
```

初期化後の操作と承認は PowerShell またはコマンドプロンプトで実行できます。承認は Codex セッションとは別の対話端末で行います。

```powershell
.\scripts\sdlc.cmd status
.\scripts\sdlc.cmd gate artifacts 00
.\scripts\approve.cmd 00
```

Codex CLI の hooks が動作するかは、実際の起動環境で確認してください。承認の TTY 検査に引っかかる場合は、Git Bash の mintty からではなく上記の端末で `.cmd` を実行します。
