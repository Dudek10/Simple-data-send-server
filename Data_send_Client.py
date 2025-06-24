import socket
import os
import struct
HOST = '192.168.0.15'
PORT = 5000

allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'txt'}

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))

try:
    while True:
        pathname = input("Podaj nazwę lub ścieżkę pliku do wysłania: ").strip()
        if pathname.lower() == 'exit':
            print("Koniec wysyłania pliku.")
            break
        if not os.path.isfile(pathname):
            print("Plik nie istnieje. Spróbuj ponownie.")
            continue
    
        filename = os.path.basename(pathname)
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip('.')
    
        if ext not in allowed_extensions:
            print(f"Format .{ext} nie jest obsługiwany. dozwolone rozszerzenia: {allowed_extensions}")
            continue
        socket_client.send(filename.encode())

        filesize = os.path.getsize(pathname)
        socket_client.send(struct.pack('!Q', filesize))

        with open(pathname, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                socket_client.send(data)
            
        print(f"Plik {filename} został wysłany.")
finally:
    socket_client.close()

                