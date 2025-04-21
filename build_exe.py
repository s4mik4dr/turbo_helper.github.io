import os
import subprocess
import sys

def main():
    print("Начинаем создание исполняемого файла ТурбоПарсер...")
    
    # Проверяем наличие PyInstaller
    try:
        import PyInstaller
        print("PyInstaller установлен!")
    except ImportError:
        print("PyInstaller не найден. Устанавливаем...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller успешно установлен!")
    
    # Запускаем сборку исполняемого файла
    print("Запускаем процесс сборки...")
    result = subprocess.run(["pyinstaller", "--noconfirm", "turboparser.spec"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           text=True)
    
    if result.returncode == 0:
        print("Сборка успешно завершена!")
        print("Исполняемый файл доступен в директории: dist/turboparser")
    else:
        print("Произошла ошибка при сборке:")
        print(result.stderr)
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Готово! Теперь вы можете запустить ТурбоПарсер через dist/turboparser/ТурбоПарсер.exe")
    else:
        print("Сборка завершилась с ошибками. Проверьте логи выше.") 