
import os

def get_files_content(directory='.'):
    """Extract file names and contents from a directory | Mengambil nama dan isi file dari direktori."""
    result = []
    # Get current folder name | Mendapatkan nama folder saat ini
    folder_name = os.path.basename(os.path.abspath(directory))
    # List of excluded folders | Daftar folder yang dikecualikan
    excluded_folders = ['node_modules', 'venv', '.git', 'dist', 'build']
    # List of excluded files | Daftar file yang dikecualikan
    excluded_files = ['package-lock.json', 'yarn.lock', '.gitignore', 'genf.py']
    # Iterate through all files in the directory | Mengiterasi semua file dalam direktori
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # Process only files (not folders) and exclude specified files | Hanya memproses file (bukan folder) dan mengecualikan file tertentu
        if os.path.isfile(file_path) and filename not in excluded_files:
            # Check if file is in excluded folders | Memeriksa apakah file berada di folder yang dikecualikan
            if not any(excluded in file_path for excluded in excluded_folders):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # Append file name and content to result | Menambahkan nama file dan isinya ke hasil
                        result.append(f"File: {filename}\n{content}\n{'='*50}\n")
                except Exception as e:
                    # Handle file reading errors | Menangani error saat membaca file
                    result.append(f"File: {filename}\nError reading file: {str(e)}\n{'='*50}\n")
    return '\n'.join(result)

def main():
    """Main function to run the script | Fungsi utama untuk menjalankan script."""
    # Get file contents from current directory | Mengambil isi file dari direktori saat ini
    output = get_files_content()
    # Get current folder name | Mendapatkan nama folder saat ini
    folder_name = os.path.basename(os.path.abspath('.'))
    # Save output to a file named after the folder | Menyimpan hasil ke file dengan nama sesuai folder
    output_file = f'{folder_name}.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    # Print confirmation message | Cetak pesan konfirmasi
    print(f"Results saved to {output_file} | Hasil telah disimpan ke {output_file}")

if __name__ == "__main__":
    main()
