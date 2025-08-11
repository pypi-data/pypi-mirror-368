import json
import os
import sys
import traceback
import inspect
from contextlib import contextmanager
import logging

# --- Конфигурация ---
ZEPPELIN_BASE_DIR = "/notebook"

# --- Вспомогательные функции ---

@contextmanager
def suppress_output(suppress_stdout=True, suppress_stderr=True):
    """
    Контекстный менеджер для временного подавления вывода и перехвата логов.
    Эта версия использует logging.disable(), чтобы избежать проблемы с закрытыми файлами.
    """
    # Сохраняем оригинальные потоки
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Сохраняем оригинальный "уровень отключения" логгера.
    # Это более надежно, чем манипулировать обработчиками.
    # Атрибут `manager.disable` хранит текущее значение, установленное logging.disable().
    manager = logging.root.manager
    original_disabled_level = manager.disable
    
    devnull = open(os.devnull, 'w', encoding='utf-8')
    
    try:
        # Перенаправляем stdout/stderr
        if suppress_stdout:
            sys.stdout = devnull
        if suppress_stderr:
            sys.stderr = devnull
        
        # Полностью отключаем все сообщения с уровнем CRITICAL и ниже.
        # Это эффективно отключает все стандартное логирование.
        logging.disable(logging.CRITICAL)
        
        yield
        
    finally:
        # Восстанавливаем оригинальные потоки
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # Восстанавливаем предыдущее состояние "отключения" логов
        logging.disable(original_disabled_level)
        
        devnull.close()

# --- Основные функции ---

def find_notebook_path(notebook_path_prefix, base_dir, verbose):
    """
    Находит полный путь к файлу ноутбука Zeppelin (.zpln) по его префиксу.
    """
    normalized_prefix = notebook_path_prefix.strip('/')
    parts = normalized_prefix.rsplit('/', 1) if '/' in normalized_prefix else ("", normalized_prefix)
    notebook_dir_relative, notebook_base_name = parts

    target_dir = os.path.join(base_dir, notebook_dir_relative)
    if verbose:
        print(f"[DEBUG] Поиск ноутбука с именем '{notebook_base_name}' в '{target_dir}'")

    if not os.path.isdir(target_dir):
        raise FileNotFoundError(f"Директория для импорта не найдена: {target_dir}")

    matches = []
    try:
        for filename in os.listdir(target_dir):
            if filename.endswith(".zpln"):
                name_without_ext = filename[:-5]
                last_underscore_index = name_without_ext.rfind('_')
                if last_underscore_index != -1 and name_without_ext[:last_underscore_index] == notebook_base_name:
                    matches.append(os.path.join(target_dir, filename))
    except OSError as e:
        raise FileNotFoundError(f"Ошибка доступа к директории {target_dir}: {e}")

    if not matches:
        raise FileNotFoundError(f"Ноутбук с префиксом '{notebook_path_prefix}' не найден в '{target_dir}'.")
    elif len(matches) > 1:
        matches_str = "\n".join(matches)
        raise ValueError(
            f"Найдено несколько ноутбуков для префикса '{notebook_path_prefix}':\n{matches_str}\n"
            "Пожалуйста, укажите более точный путь."
        )
    
    if verbose:
        print(f"[DEBUG] Найден один совпадающий ноутбук: {matches[0]}")
    return matches[0]


def import_zeppelin_notebook_from_path(full_notebook_path, verbose, show_link):
    """
    Внутренняя функция для выполнения кода из файла ноутбука.
    """
    try:
        if verbose:
            print(f"[DEBUG] Читаю файл: {full_notebook_path}")

        if not os.path.exists(full_notebook_path):
            print(f"ОШИБКА: Файл ноутбука не найден: {full_notebook_path}")
            return False

        with open(full_notebook_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        python_code_to_execute = ""
        found_python_paragraph = False

        if verbose:
            print("[DEBUG] Начало анализа параграфов...")
        
        for i, paragraph in enumerate(notebook_data.get("paragraphs", [])):
            paragraph_index = i + 1
            code = paragraph.get("text", "")
            
            # Логика анализа параграфа, которая будет выводиться в verbose-режиме
            def analyze_paragraph(is_python_para):
                print(f"\n[DEBUG] Анализ параграфа #{paragraph_index}:")
                if not code or not code.strip():
                    print("[DEBUG] -> Статус: Пустой, пропускается.")
                    return False
                
                first_line = code.splitlines()[0]
                print(f"[DEBUG] -> Первая строка: '{first_line}'")
                if is_python_para:
                    print("[DEBUG] -> Статус: Python-параграф, будет включен в импорт.")
                else:
                    print("[DEBUG] -> Статус: Не Python-параграф, пропускается.")
                return True

            is_python = False
            if code.lstrip().startswith(("%python", "%spark.pyspark", "%flink.pyflink", "%jdbc(python)")):
                is_python = True
                
            if verbose:
                analyze_paragraph(is_python)
            
            if is_python:
                found_python_paragraph = True
                lines = code.splitlines()
                if len(lines) > 1:
                    actual_code = "\n".join(lines[1:])
                    if actual_code.strip():
                        python_code_to_execute += actual_code + "\n\n"

        if verbose:
            print("\n[DEBUG] Анализ параграфов завершен.")

        if python_code_to_execute:
            caller_globals = inspect.stack()[2].frame.f_globals
            
            if verbose:
                print("-" * 20 + "\n[DEBUG] Итоговый код для выполнения:\n" + python_code_to_execute.strip() + "\n" + "-" * 20)
                exec(python_code_to_execute, caller_globals)
                print(f"[DEBUG] Выполнение кода из {os.path.basename(full_notebook_path)} завершено.")
            else:
                with suppress_output():
                    exec(python_code_to_execute, caller_globals)
            
        elif verbose:
            if found_python_paragraph:
                print(f"[DEBUG] В ноутбуке найдены Python-параграфы, но они не содержат исполняемого кода.")
            else:
                print(f"[DEBUG] В ноутбуке не найдено ни одного Python-параграфа.")
        
        # Генерация и вывод ссылки в самом конце, если требуется
        if show_link:
            try:
                filename = os.path.basename(full_notebook_path)
                name_without_ext = filename[:-5]
                last_underscore_index = name_without_ext.rfind('_')
                if last_underscore_index != -1:
                    notebook_id = name_without_ext[last_underscore_index + 1:]
                    relative_url = f"#/notebook/{notebook_id}"
                    clean_notebook_name = name_without_ext[:last_underscore_index]
                    print(
                        f'%html <div style="font-family: Arial, sans-serif; font-size: 14px; margin-top: 5px; margin-bottom: 5px;"><strong>Импортирован ноутбук:</strong> <a href="{relative_url}" '
                        f'target="_blank" rel="noopener noreferrer">{clean_notebook_name}</a></div>'
                    )
            except Exception as link_err:
                if verbose:
                    print(f"[DEBUG] Не удалось создать ссылку на ноутбук: {link_err}")
        
        return True

    except Exception:
        traceback.print_exc()
        return False


# --- Публичная API-функция ---

def import_note(notebook_path_prefix, base_dir=ZEPPELIN_BASE_DIR, verbose=False, show_link=True):
    """
    Находит и выполняет Python-код из другого ноутбука Zeppelin, делая его
    определения (функции, переменные) доступными в текущей сессии.
    Ничего не возвращает, чтобы избежать авто-печати 'True' в Zeppelin.
    
    :param notebook_path_prefix: Путь-префикс к ноутбуку для импорта (например, 'libraries/utils').
    :param base_dir: (опционально) Базовая директория ноутбуков.
    :param verbose: (опционально) Если True, выводит подробный лог выполнения. По умолчанию False.
    :param show_link: (опционально) Если True, выводит кликабельную ссылку на импортированный ноутбук. По умолчанию True.
    """
    try:
        full_path = find_notebook_path(notebook_path_prefix, base_dir, verbose)
        import_zeppelin_notebook_from_path(full_path, verbose, show_link)
    except (FileNotFoundError, ValueError) as e:
        print(f"ОШИБКА ИМПОРТА: {e}")
    except Exception:
        print(f"НЕПРЕДВИДЕННАЯ ОШИБКА при импорте '{notebook_path_prefix}':")
        traceback.print_exc()