# Готовый Docker image для RunPod

Наглядная версия с кнопками копирования: [RUNPOD_GUIDE.html](RUNPOD_GUIDE.html).
Откройте HTML-файл в браузере; интернет для самой инструкции не нужен.

В образе находятся CUDA/PyTorch, закреплённые Git-версии ComfyUI и Manager,
зависимости панели, SQLite-каталог и загрузчик. При запуске `git pull` и
`pip install` не выполняются. Сначала образ проверяет сохранённые версии
пакетов и импорты.
Если окружение повреждено, запуск завершается с ошибкой вместо переустановки.

Код работает из `/opt/ComfyUI`, поэтому тысячи небольших файлов Python не
читаются с network volume. Модели, input, output, user/workflows, API JSON,
логи и временные загрузки связаны с `/workspace/ComfyUI`. Уже имеющиеся модели
и результаты сохраняются. Старый код в `/workspace/ComfyUI` не используется
и не удаляется. Тяжёлые HF/Torch-кэши также находятся в `/workspace/.cache`.

## 1. Сборка и публикация через GitHub

### Отправить изменения самостоятельно

Из корня репозитория выполнить:

```bash
git add .gitignore .dockerignore Dockerfile .github/workflows/docker-image.yml \
  RUNPOD_IMAGE.md RUNPOD_STARTUP.md RUNPOD_GUIDE.html docker/ \
  comfy_install_runpod.sh comfy_control_panel.py runpod_startup.sh \
  comfy_template_startup.py tests/test_runpod_install.py \
  tests/test_image_storage.py tests/test_startup_environment.py \
  tests/test_template_api_export.py
git commit -m "Add preinstalled ComfyUI image for RunPod"
git push origin main
```

Можно отправить эти файлы через используемый Git-клиент. Команды рассчитаны
на текущую ветку `main`; при работе в другой ветке сначала влить изменения в `main`,
чтобы workflow появился в списке Actions. Файл `.env.secrets`, модели и локальные
логи не входят в список отправляемых файлов.

### Собрать и опубликовать image

После отправки изменений:

1. Открыть **Actions → Build RunPod image → Run workflow**.
2. Указать новый номер, например `v1.0.0`, и запустить.
3. Workflow соберёт `linux/amd64`, проверит контейнер без GPU и опубликует:
   `ghcr.io/dizzle700/comfyui-runpod:v1.0.0`.
4. В GitHub открыть пакет **comfyui-runpod → Package settings → Change visibility → Public**.
   Для приватного пакета вместо этого добавить GHCR credentials в RunPod.

Открыть workflow: [Build RunPod image](https://github.com/Dizzle700/ComfyUI-runpod/actions/workflows/docker-image.yml).
После успешного выполнения точное имя image появится в **Summary** этого запуска.
Использовать его в RunPod только после успешной сборки и публикации.

`GITHUB_TOKEN` создаётся GitHub автоматически; отдельный токен для публикации
из Actions не нужен. Workflow также запускается при push Git-тега `v1.0.0`.
Если номер не указан при ручном запуске, публикуется только тег `sha-<полный SHA>`.
Первую сборку нужно дождаться: скачивание CUDA-базы и установка зависимостей
выполняются во время сборки. Секреты и локальные модели исключены из build context.

## 2. Настройки RunPod Template

| Поле | Значение |
| --- | --- |
| Container Image | `ghcr.io/dizzle700/comfyui-runpod:v1.0.0` после успешной публикации |
| Docker Command / Container Start Command | Оставить пустым: запуск уже в image |
| Volume Mount Path | `/workspace` |
| HTTP ports | `7860`, `8188` |
| TCP port | `22`, если нужен SSH |

Переменные окружения:

```dotenv
PANEL_USER=admin
PANEL_PASS=<свой пароль через RunPod Secret>
COMFY_TEMPLATE_IDS=89,93,94
COMFY_TEMPLATE_DOWNLOAD_WORKERS=2
AUTO_START_COMFY=1
```

89 — Krea-2 Turbo; 93 — Qwen-Image 2512; 94 — Qwen-Image.
Это пример: можно указать любые существующие ID из `templates_models.db`.
API JSON экспортируются сразу, модели скачиваются отдельным процессом с двумя
параллельными загрузками. Уже имеющиеся непустые файлы пропускаются.
Неисполняемые заметки `Note` / `MarkdownNote` удаляются из API JSON при экспорте;
в визуальном workflow они сохраняются. Другие custom nodes остаются обязательными.
`HF_TOKEN` и `CIVITAI_API_TOKEN` добавлять через Secrets, если источник требует доступ.

Для старых пакетов из `KRea.txt` доступна переменная `COMFY_MODEL_PACKAGES=Krea`;
она скачивает модели до запуска панели. Для фоновой загрузки использовать ID
шаблонов. CLI-флаги `--templates` и `--models` также работают через аргументы
entrypoint; переменные окружения удобнее для RunPod Template.

Network volume позволяет использовать модели при пересоздании Pod. Обычный
volume disk сохраняется при stop/start, но удаляется при terminate.
Первый старт на новом хосте может включать скачивание самого image. Существующая
модель на диске готова к работе только после запуска ComfyUI и наличия её узлов.

## 3. Подключение

Панель: `https://POD_ID-7860.proxy.runpod.net`.
ComfyUI и его API: `https://POD_ID-8188.proxy.runpod.net`.

Состояние выбранных шаблонов (Basic Auth):

```bash
curl -u "$PANEL_USER:$PANEL_PASS" \
  https://POD_ID-7860.proxy.runpod.net/template-apis
curl -u "$PANEL_USER:$PANEL_PASS" \
  https://POD_ID-7860.proxy.runpod.net/template-apis/89/api > 89.api.json
```

Для генерации дождаться `ready: true`, изменить промпт в JSON и отправить
`{"prompt": ...}` на ComfyUI `POST /prompt`; пример в [RUNPOD_STARTUP.md](RUNPOD_STARTUP.md).
Пароль панели защищает порт 7860. Порт 8188 сохраняет обычный ComfyUI API
без этой авторизации; для закрытого доступа использовать SSH tunnel и не
публиковать 8188 через HTTP proxy.

## Локальная сборка и проверка

```bash
docker build --platform=linux/amd64 -t comfyui-runpod:dev .
bash docker/smoke-test.sh comfyui-runpod:dev
```

Smoke test запускает ComfyUI в CPU-режиме и проверяет импорты, узлы трёх
примерных шаблонов, сохранность файлов, API с авторизацией и повторный
старт; модели заменены временными заглушками. Генерация и доступность GPU в этом
тесте не проверяются. Docker healthcheck показывает готовность панели; статус
генерации смотреть через `/template-apis` и ComfyUI.

При ручной публикации переименовать image в свой GHCR/Docker Hub registry,
выполнить `docker login`, затем `docker push`. Можно посмотреть установленные
версии через `docker run --rm --entrypoint cat comfyui-runpod:dev /opt/image-versions.json`
и `/opt/python-packages.txt`.

## Обновления и custom nodes

Для обновления изменить SHA `COMFY_COMMIT` / `MANAGER_COMMIT` в Dockerfile,
собрать и опубликовать **новый** тег, затем пересоздать Pod с тем же network volume.
База закреплена digest, Git — полными SHA. Python-пакеты фиксируются внутри
построенного image, их полный список сохраняется в `/opt/python-packages.txt`.
Новая сборка может разрешить другие версии незакреплённых транзитивных зависимостей;
для повторного запуска абсолютно того же окружения использовать опубликованный
digest `ghcr.io/...@sha256:...` из вывода `docker push`.

`--update`, `--reinstall` и кнопка установки ComfyUI в панели предлагают
пересборку образа. Custom nodes, установленные в работающем контейнере через
панель/Manager, относятся к container disk и исчезают при пересоздании Pod;
если они меняют уже закреплённые пакеты, проверка следующего старта сообщит об
изменении окружения. Постоянный набор custom nodes и его зависимости нужно
добавить в Dockerfile **до сохранения `.runpod-setup.json`**. Workflow JSON и
модели сохраняются на volume независимо от этого.

Основа схемы: [официальный RunPod guide по custom templates](https://docs.runpod.io/pods/templates/create-custom-template).
