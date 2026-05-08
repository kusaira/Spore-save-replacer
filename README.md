# Spore Save Replacer

Простая программа на Python с графическим интерфейсом `tkinter`.

Она копирует все файлы и папки из локальной папки `Spore`, которая лежит рядом с программой, в папку текущего пользователя Windows:

```text
C:\Users\<username>\AppData\Roaming\Spore
```

Если папки назначения нет, программа создаст ее автоматически. Если папка уже существует, ее содержимое будет заменено содержимым локальной папки `Spore` без дополнительных вопросов.

## Структура папки

Рядом с `spore_replacer.py` или собранным `.exe` должна лежать папка `Spore`:

```text
program-folder/
  spore_replacer.py
  Spore/
    ...
```

После сборки в `.exe` структура должна быть такой:

```text
program-folder/
  spore_replacer.exe
  Spore/
    ...
```

## Запуск из Python

Требуется Python 3.8+.

```powershell
python spore_replacer.py
```

## Сборка в .exe через PyInstaller

Установить PyInstaller:

```powershell
python -m pip install pyinstaller
```

Собрать один `.exe`:

```powershell
pyinstaller --onefile --windowed --name spore_replacer spore_replacer.py
```

Готовый файл будет здесь:

```text
dist\spore_replacer.exe
```

Скопируйте папку `Spore` рядом с `dist\spore_replacer.exe`, чтобы программа могла найти файлы для замены.

## Настройка "Do not ask again"

Если пользователь нажал `Yes` и отметил `Do not ask again`, настройка сохраняется в:

```text
C:\Users\<username>\AppData\Roaming\SporeSaveReplacer\settings.json
```

При следующих запусках предупреждение будет пропущено.
