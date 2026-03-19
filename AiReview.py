import subprocess
import os
import sys
import json
import anthropic
import openai
from datetime import datetime

def load_settings():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(exe_dir, 'appsettings.json')
    if not os.path.exists(path):
        print(f"Ошибка: Файл настроек не найден по пути: {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

settings = load_settings()

def decode_output(binary_data):
    for codec in ['utf-8', 'cp1251', 'cp866']:
        try: return binary_data.decode(codec)
        except UnicodeDecodeError: continue
    return binary_data.decode('utf-8', errors='replace')

def get_diff_git():
    cfg = settings["ProjectSettings"]
    context = cfg.get("ContextLines", 0)
    files = subprocess.check_output(["git", "diff", "--name-only", "--staged"]).decode("utf-8", errors="replace").splitlines()
    diffs = []
    for f in files:
        if any(f.endswith(ext) for ext in cfg["AllowedExtensions"]) and not any(p in f for p in cfg["IgnoredPatterns"]):
            d = subprocess.check_output(["git", "diff", "--staged", f"-U{context}", "--", f])
            diffs.append(f"### File: {f}\n```diff\n{decode_output(d)}\n```")
    return "\n\n".join(diffs)

def get_diff_tfs():
    cfg = settings["ProjectSettings"]
    tfs_exe = settings["ProjectSettings"]["TfsExePath"]
    
    try:
        status_raw = subprocess.check_output([tfs_exe, "status", "/recursive", "/noprompt", "."], stderr=subprocess.STDOUT)
        status_text = decode_output(status_raw)
        
        diffs = []
        for line in status_text.splitlines():
            if ":" not in line: continue
            
            line = line.strip()
            parts = line.split(":", 1)
            if len(parts) < 2: continue

            full_path = (line[line.find(":")-1:]).strip()
            # Убираем возможные метки в конце пути
            if " [" in full_path: full_path = full_path.split(" [")[0].strip()

            # Фильтрация по расширениям
            file_name = os.path.basename(full_path)
            if any(full_path.lower().endswith(ext.lower()) for ext in cfg["AllowedExtensions"]) and \
               not any(p.lower() in full_path.lower() for p in cfg["IgnoredPatterns"]):
                
                content = ""
                try:
                    d_raw = subprocess.check_output([tfs_exe, "diff", "/noprompt", full_path], stderr=subprocess.STDOUT)
                    content = decode_output(d_raw)
                except subprocess.CalledProcessError as e:
                    if e.returncode == 1: content = decode_output(e.output)

                if content.strip():
                    clean_lines = []
                    # Убираем мусорные строки TFS, оставляем только сам diff
                    for c_line in content.splitlines():
                        skip_keywords = ["====", "Retrieving", "Local path", "Server path", "Index:","Изменение:", 
                                         "изменение:","добавление:", "--- [no source file]", "--- Сервер:", "+++ Локальные:","Файл:", "файл:"]
                        if not any(k in c_line for k in skip_keywords):
                            clean_lines.append(c_line)
                    
                    clean_content = "\n".join(clean_lines).strip()
                    
                    # Добавляем в список только имя файла и чистый код
                    diffs.append(f"### FILE: {file_name}\n```diff\n{clean_content}\n```")

        return "\n\n".join(diffs) if diffs else None

    except Exception as e:
        raise ValueError(f"Ошибка TFS: {str(e)}")
    
def call_anthropic(promt):
    client = anthropic.Anthropic(api_key=settings["ApiKey"])
    msg = client.messages.create(
        model=settings["Model"],
        max_tokens=4096,
        messages=[{"role": "user", "content": promt}]
    )
    return msg.content[0].text

def call_openai_compatible(promt):
    client = openai.OpenAI(api_key=settings["ApiKey"], base_url=settings.get("BaseUrl"))
    resp = client.chat.completions.create(
        model=settings["Model"],
        messages=[{"role": "user", "content": promt}]
    )
    return resp.choices[0].message.content

def get_ai_review(diff_text, vcs_type):
    if not diff_text or len(diff_text.strip()) < 10: return None
    provider = settings.get("Provider")
    full_prompt = settings["AiPrompt"].format(vcs_type=vcs_type, diff_text=diff_text)

    if provider == "Anthropic":
        return call_anthropic(full_prompt)
    elif provider in ["OpenAI"]:
        return call_openai_compatible(full_prompt)
    else:
        return "Ошибка: Неизвестный провайдер в appsettings.json"

if __name__ == "__main__":
    try:
        p_path = input("Путь к проекту: ").strip().replace('"', '')
        if not os.path.isdir(p_path): sys.exit("Путь не найден.")
        os.chdir(p_path)

        vcs = input("1 - Git, 2 - TFS: ").strip()
        vcs_name = "Git (Unified Diff)" if vcs == "1" else "TFS (TFVC)"
        print("Собираю изменения...")
        content = get_diff_git() if vcs == "1" else get_diff_tfs()

        if content:
            print(f"Запрос к {settings['Provider']}...")
            #review = get_ai_review(content, vcs_name)
            review = content
            if review:
                script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                project_name = os.path.basename(p_path.rstrip(os.sep))
                date = datetime.now().strftime('%Y-%m-%d_%H-%M')
                fname = f"{project_name}_{date}.md"
                reports_dir = os.path.join(script_dir, "Reviews")
                os.makedirs(reports_dir, exist_ok=True)
                full_path = os.path.join(reports_dir, fname)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(f"# Code Review Report: {project_name}\n")
                    f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("\n---\n\n")
                    f.write(review)
                print(f"Готово! Результат в {fname}")
                choice = input("\nОткрыть файл ревью? (y/n): ").strip().lower()
                if choice == 'y':
                    print("Открываю файл...")
                    os.startfile(full_path)
                else:
                    print("Файл сохранен. До свидания!")
        else:
            print("Изменений нет.")
    except Exception as e:
        print(f"Error: {e}")
        input()