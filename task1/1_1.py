import os

def get_file_extension(filename):
    if '.' not in filename:
        print("File has no extension")
        return None
    return os.path.splitext(filename)[1]

filename = input("Enter the filename: ")
extension = get_file_extension(filename)
if(extension != None):
    print("File extension:", extension)