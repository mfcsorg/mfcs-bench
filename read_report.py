import sys

def try_read_file(file_path, encodings=['utf-8', 'gbk', 'gb2312', 'gb18030']):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                print(f"\nSuccessfully read with {encoding} encoding:\n")
                print(content)
                return
        except UnicodeDecodeError:
            continue
    print("Failed to read file with any of the attempted encodings")

if __name__ == "__main__":
    report_path = "reports/report_20250430_161618.md"
    try_read_file(report_path) 