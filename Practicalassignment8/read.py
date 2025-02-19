file_path = "/var/ftp/pub/known_good.txt"
with open(file_path, 'r') as file:
    data = file.read()
    # Process data as needed
    print(data)
