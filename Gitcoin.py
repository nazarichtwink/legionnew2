import os
import time
import random
import subprocess
import requests
from loguru import logger

# =========== КОНФІГУРАЦІЯ ===========
GITHUB_REPO = "nazarichtwink/legionnew2"  # Ваш новий репозиторій
GITHUB_USER_NAME = os.getenv("GITHUB_USER", "nazarichtwink")  # fallback, якщо не задано
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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")  # Має бути задано перед запуском
GITHUB_USER_EMAIL = "nazarichtwink@gmail.com"  # Пошта, прив'язана до GitHub
FILE_TYPES = ['.py', '.js', '.html', '.md']

logger.add("smart_commit.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")


def setup_git_config():
    """Налаштування глобальних параметрів Git (ім’я та email)"""
    subprocess.run(["git", "config", "--global", "user.name", GITHUB_USER_NAME], check=True)
    subprocess.run(["git", "config", "--global", "user.email", GITHUB_USER_EMAIL], check=True)
    logger.info("Git config оновлено")


def generate_random_sentence():
    """Генерація природнього тексту для коментарів"""
    subjects = ["Додано", "Виправлено", "Оновлено", "Покращено"]
    objects = ["функціонал", "документацію", "інтерфейс", "логіку"]
    return f"{random.choice(subjects)} {random.choice(objects)} {int(time.time())}"


def generate_meaningful_content(file_type):
    """Генерація правдоподібного контенту"""
    templates = {
        '.py': f"# {generate_random_sentence()}\ndef main():\n    print('Hello World')\n",
        '.js': f"// {generate_random_sentence()}\nfunction main() {{\n  console.log('Hi');\n}}\n",
        '.html': f"<!-- {generate_random_sentence()} -->\n<html>\n<body>\n<h1>Test</h1>\n</body>\n</html>",
        '.md': f"# {generate_random_sentence()}\n\nАвтоматично створений документ"
    }
    return templates.get(file_type, "Default content")


def create_files():
    """Створення файлу з випадковим розширенням"""
    try:
        file_type = random.choice(FILE_TYPES)
        filename = f"file_{int(time.time())}{file_type}"

        with open(filename, 'w', encoding='utf-8') as f:
            content = generate_meaningful_content(file_type)
            f.write(content)

        logger.info(f"Створено {filename}")
        return filename
    except Exception as e:
        logger.error(f"Помилка створення файлу: {e}")
        return None


def make_commit():
    """Виконання коміту та пушу"""
    try:
        # Перевірка: якщо токена немає, пуш не вдасться
        if not GITHUB_TOKEN:
            logger.error("Не задано GITHUB_TOKEN! Встановіть змінну оточення і перезапустіть.")
            return False

        filename = create_files()
        if not filename:
            return False

        # Якщо .git відсутній – ініціалізуємо репо і додаємо origin
        if not os.path.exists(".git"):
            logger.info("Ініціалізація Git репозиторію...")
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "branch", "-M", "main"], check=True)

            remote_url = f"https://{GITHUB_USER_NAME}:{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

        subprocess.run(["git", "add", "."], check=True)
        commit_msg = generate_random_sentence()
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

        logger.success(f"Успішний коміт: {commit_msg}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Помилка Git: {e}")
        return False


def create_meaningful_pr():
    """Створення Pull Request (демо-функціонал)"""
    try:
        if not GITHUB_TOKEN:
            logger.error("Не задано GITHUB_TOKEN, PR не буде створено.")
            return

        branch_name = f"feature-{int(time.time())}"
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

        with open("README.md", "a", encoding='utf-8') as f:
            f.write(f"\n\n## Нова функція {branch_name}\nОпис змін...")

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Додано нову функцію: {branch_name}"], check=True)
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

        url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        data = {
            "title": f"Нова функція: {branch_name}",
            "head": branch_name,
            "base": "main",
            "body": "Цей PR додає новий функціонал."
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            logger.success(f"PR створено: {response.json()['html_url']}")
        else:
            logger.error(f"Помилка PR: {response.text}")

    except Exception as e:
        logger.error(f"Помилка створення PR: {e}")


def main():
    setup_git_config()
    try:
        while True:
            if make_commit():
                # Випадковий перелік дій: або створює PR, або чекає 30–60 с між комітами
                actions = [
                    lambda: create_meaningful_pr(),
                    lambda: time.sleep(random.randint(30, 60))
                ]
                random.choice(actions)()
    except KeyboardInterrupt:
        logger.info("Роботу зупинено")


if __name__ == "__main__":
    main()
