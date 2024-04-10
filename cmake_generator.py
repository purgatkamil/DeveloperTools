import os
import subprocess
import shutil
from tkinter import filedialog, Tk, messagebox

def copy_files_to_output_directory(output_file_path):

    # Pobierz ścieżkę bieżącego katalogu
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Utwórz ścieżkę do katalogu o jeden poziom niżej
    target_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

    print(target_directory)

    # Pobierz ścieżkę folderu docelowego, gdzie ma być zapisany plik CMakeLists.txt
    output_directory = os.path.dirname(output_file_path)
    
    # Ścieżki plików źródłowych do skopiowania
    source_files = ["compiler_flags.cmake", "gcc-arm-none-eabi.cmake", "Makefile"]
    
    for source_file in source_files:
        source_path = os.path.join("", source_file)
        destination_path = os.path.join(output_directory, source_file)
        
        # Sprawdź, czy plik już istnieje w folderze docelowym
        if os.path.exists(destination_path):
            print(f"Ostrzeżenie: Plik {source_file} już istnieje w folderze docelowym.")
            continue
        
        # Kopiuj plik źródłowy do folderu docelowego
        try:
            shutil.copyfile(source_path, destination_path)
            print(f"Plik {source_file} został skopiowany do folderu docelowego.")
        except Exception as e:
            print(f"Błąd podczas kopiowania pliku {source_file}: {e}")


def find_files(directory, extension):
    """
    Przeszukuje podany katalog i subkatalogi w poszukiwaniu plików z rozszerzeniem extension.
    Zwraca listę względnych ścieżek do folderów zawierających znalezione pliki nagłówkowe,
    względem podanego katalogu.
    """
    folders = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                full_path = os.path.join(root, file)
                # Obliczanie ścieżki względnej folderu
                folder_path = os.path.dirname(os.path.relpath(full_path, directory))
                if not folder_path:  # Jeśli folder_path jest pusty, oznacza to, że plik jest w folderze root.
                    folder_path = "."  # Użyj "." jako oznaczenia folderu root.
                folders.add(folder_path.replace(os.sep, '/'))
    return list(folders)



def select_directory(title="Select a directory"):
    """
    Wyświetla okno dialogowe umożliwiające użytkownikowi wybranie katalogu.
    """
    root = Tk()
    root.withdraw()  # Nie pokazujemy głównego okna
    directory = filedialog.askdirectory(title=title)  # Otwieramy dialog wyboru folderu
    root.destroy()  # Zamykamy instancję Tkinter
    return directory 

def save_paths_to_file(folders):
    """
    Wyświetla okno dialogowe umożliwiające użytkownikowi wybranie ścieżki i nazwy pliku,
    do którego zostaną zapisane ścieżki.
    """
    cmake_config1 = [
        "cmake_minimum_required(VERSION 3.14)\n\n",
        "set(CMAKE_TOOLCHAIN_FILE gcc-arm-none-eabi.cmake)\n\n",
        "enable_language(ASM)\n\n",
        "project(nazwa_projektu)\n\n"
    ]

    cmake_config2 = [
        "set(GLOBAL_DEFINES\n-DDEBUG\n-DUSE_HAL_DRIVER \n-DSTM32L073xx\n)\n\n",
        "set(LINKED_LIBS\n\n)\n\n",
        "\nlink_directories(\n\n)\n\n",
        "include_directories(${INCLUDE_DIRS})\n\n",
        "include(compiler_flags.cmake)\n\n",
        "add_definitions(${GLOBAL_DEFINES})\n\n",
        "add_executable(nazwa_projektu ${CPP_SRCS} ${C_SRCS} ${ASM_SRCS})\n\n",
        "link_libraries(nazwa_projektu ${LINKED_LIBS})\n\n"
    ]

    root = Tk()
    root.withdraw()
    filename = "CMakeLists.txt"
    filepath = filedialog.askdirectory(title="Select Directory")
    filepath = os.path.join(filepath, filename)

    if os.path.exists(filepath):
        # Jeśli plik już istnieje, pyta użytkownika, czy nadpisać
        want_to_overwrite = messagebox.askyesno("Plik istnieje", "Plik o nazwie \"CMakeLists.txt\" istnieje w wybranym katalogu. Nadpisać plik?")
        if not want_to_overwrite:
            messagebox.showinfo("Zapisywanie anulowane")
            return

    root.destroy()
    if filepath:
        with open(filepath, "w") as file:

            file.writelines(cmake_config1)

            # Zapisz ścieżki plików .c
            if folders['c']:
                file.write("set(C_SRC \n")
                for path in sorted(folders['c']):
                    file.write(f"    {path}/\n")
                file.write(")\n\n")
            
            # Zapisz ścieżki plików .h
            if folders['h']:
                file.write("set(INCLUDE_DIRS \n")
                for path in sorted(folders['h']):
                    file.write(f"    {path}/\n")
                file.write(")\n\n")

            # Zapisz ścieżki plików .s
            if folders['s']:
                file.write("set(ASM_SRCS \n")
                for path in sorted(folders['s']):
                    file.write(f"    {path}/\n")
                file.write(")\n\n")

            # Zapisz ścieżki plików .ld
            if folders.get('ld', []):
                file.write("set(LD_SCRIPT \n")
                for path in sorted(folders['ld']):
                    file.write(f"    {path}/\n")
                file.write(")\n\n")

            file.writelines(cmake_config2)

        copy_files_to_output_directory(filepath)
        messagebox.showinfo("Zakończono operację", "Plik zapisany")
        subprocess.run(['notepad', filepath])
            


if __name__ == "__main__":
    selected_directory = select_directory("Select the directory to search for files")
    if selected_directory:
        folders = {
            'h': find_files(selected_directory, ".h"),
            'c': find_files(selected_directory, ".c"),
            's': find_files(selected_directory, ".s"),
            'ld': find_files(selected_directory, ".ld")
        }
        save_paths_to_file(folders)
    else:
        print("Nie wybrano folderu.")
