# 🤖 AI Code Reviewer | RU
Консольная утилита на Python для автоматического анализа изменений в коде (Diff) с использованием Large Language Models (Gemini, Claude, OpenAI). Поддерживает работу как с современным Git, так и с классическим TFS (TFVC).

## 🚀 Основные возможности
 - Извлечение изменений из Git (Staged) или TFS (Pending Changes).
 - Возможность выбора провайдера и Ai моделей
 - Умная фильтрация: Игнорирование служебных файлов (.Designer.cs, obj/, bin/) и фокус только на нужном коде (.cs, .sql).
 - Markdown Отчеты: Результат ревью сохраняется в файл и может быть открыт сразу после генерации.
 - Очистка лишних заголовков и метаданных перед отправкой в ИИ.

## 🛠 Настройка (appsettings.json)
Перед запуском отредактируйте файл appsettings.json в корне программы:

### Описание полей

| Поле | Описание |
|---|---|
| `Provider` | `OpenAI` — для всех OpenAI-совместимых API (включая OpenRouter, Google AI Studio и др.). `Anthropic` — для прямого использования Claude |
| `ApiKey` | API-ключ. Можно получить на [OpenRouter](https://openrouter.ai/), [Google AI Studio](https://aistudio.google.com/) и др. |
| `BaseUrl` | Адрес API-провайдера. Примеры: `https://generativelanguage.googleapis.com/v1beta/openai/`, `https://openrouter.ai/api/v1`, `https://api.openai.com/v1` |
| `Model` | Название модели: `google/gemini-2.0-flash-001`, `claude-3-5-sonnet-20241022`, `gpt-4o` и т.д. |
| `AllowedExtensions` | Список расширений файлов, которые будут отправлены на ревью |
| `IgnoredPatterns` | Паттерны файлов и папок, которые нужно исключить |
| `TfsExePath` | Путь до `TF.exe`. Нужен, если TFS не добавлен в `PATH`. Пример: `C:\Program Files\Microsoft Visual Studio\...\TF.exe` |
| `ContextLines` | Число строк контекста вокруг изменений (только для Git; в TFS не поддерживается) |
| `AiPrompt` | Промт для ии модели. Можно изменить под себя, а так-же оперировать двумя пременными `{vcs_type}` - системы контроля версий. `{diff_text}` - изменения  |

## 📖 Как пользоваться
 1. Скачайте `Release.zip` из [последнего релиза](https://github.com/NPrynia/AiReview/releases/). Распакуйте, настройте appsettings.json. Запустите ai_reviewer.exe.
 2. Вставьте путь к локальной папке вашего проекта.
 3. Выберите тип источника:
    - Git: Будут проанализированы только файлы, добавленные в индекс (git add).
    - TFS: Будут проанализированы все изменения.
 4. Дождитесь ответа ИИ и нажмите y, чтобы открыть Markdown-отчет.

![example](https://github.com/user-attachments/assets/6851102e-f411-441d-8ef0-d29bd3cf8d17)


-----------



# 🤖 AI Code Reviewer | ENG
A Python-based CLI utility for automated code change analysis (Diff) using Large Language Models (Gemini, Claude, OpenAI). It supports both modern Git and legacy TFS (TFVC) workflows.

## 🚀 Key Features
 - Dual VCS Support: Extract changes from Git (Staged) or TFS (Pending Changes).
 - Flexible AI Integration: Choose between different providers and specific AI models.
 - Smart Filtering: Automatically ignores boilerplate and system files (.Designer.cs, obj/, bin/) to focus on relevant code (.cs, .sql, etc.).
 - Markdown Reports: Analysis results are saved to a file and can be opened immediately after generation.
 - Data Scrubbing: Automatically strips unnecessary headers and metadata before sending code to the AI to save tokens and improve focus.

## 🛠 Configuration (appsettings.json)
Before running the application, configure the appsettings.json file in the root directory.


### Описание полей

| Поле | Описание |
|---|---|
| `Provider` | OpenAI / Anthropic. Use OpenAI if your provider supports the OpenAI-compatible Python SDK (e.g., Google Gemini, OpenRouter). Use Anthropic for native Claude models. |
| `ApiKey` | Your API key. You can obtain one from OpenRouter, Google AI Studio, OpenAI, etc. |
| `BaseUrl` | The API endpoint for your provider. Exemple: [https://generativelanguage.googleapis.com/v1beta/openai/], [https://openrouter.ai/api/v1], or [https://api.openai.com/v1] |
| `Model` | The specific model identifier. Exemple: `google/gemini-2.0-flash-001`, `claude-3-5-sonnet-20241022`, `gpt-4o` и т.д. |
| `AllowedExtensions` |  A whitelist filter for file types to be analyzed. |
| `IgnoredPatterns` | A blacklist filter for files or directories to be skipped. |
| `TfsExePath` | Since tf.exe is usually not in the system PATH, provide the full path to your TF.exe or ensure it is accessible. |
| `ContextLines` | Number of lines of code to include before and after the change (Note: Not currently supported for TFS). |
| `AiPrompt` | Prompt for AI models. Can be customized, and also operates with two variables: {vcs_type} - control system. {diff_text} - changes  |

---

## 📖 How to Use
Download Release.zip from the [Latest Release](https://github.com/NPrynia/AiReview/releases/).
1. Extract the archive and configure your appsettings.json.
2. Launch ai_reviewer.exe.
3. Paste the local path to your project folder.
4. Select the source type:
 - Git: Analyzes only staged files (git add).
 - TFS: Analyzes all changes.
5. Wait for the AI response and press y to open the Markdown report.
