"""PostToolUse hook: collectstatic after edits to shop/static/**.

Под CompressedManifestStaticFilesStorage правки CSS/JS/шрифтов не видны на сайте,
пока не прогнан collectstatic, а url() на отсутствующий файл роняет collectstatic
жёстко. Этот хук запускает сборку сразу после правки статики и громко сообщает,
если сборка упала. На нестатических правках выходит молча (exit 0).

Читает JSON события из stdin, печатает JSON ответа в stdout (см. схему хуков).
"""
import json
import os
import subprocess
import sys


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return  # не ломаем инструмент из-за кривого ввода

    tool_input = event.get("tool_input") or {}
    file_path = (tool_input.get("file_path") or "").replace("\\", "/")

    # Триггер только на исходную статику приложения, не на собранный staticfiles/.
    if "/shop/static/" not in file_path:
        return

    hooks_dir = os.path.dirname(os.path.abspath(__file__))        # .../.claude/hooks
    repo_root = os.path.dirname(os.path.dirname(hooks_dir))        # корень репозитория
    manage_dir = os.path.join(repo_root, "internetshop")          # где лежит manage.py

    result = subprocess.run(
        [sys.executable, "manage.py", "collectstatic", "--noinput", "-v", "0"],
        cwd=manage_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip()[-1500:]
        print(json.dumps({
            "systemMessage": "collectstatic УПАЛ — правка статики не применена:\n" + tail,
        }))
        return

    # Успех — тихо, чтобы не шуметь при серии правок.
    print(json.dumps({"suppressOutput": True}))


if __name__ == "__main__":
    main()
