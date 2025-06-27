import socket
import os
import struct
import hashlib

HOST = '127.0.0.1'
PORT = 5000
MAX_SIZE = 10485760
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif', 'txt'}

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect((HOST, PORT))

password = input("🔑 Podaj hasło dostępu: ").strip()
password_hash = hashlib.sha512(password.encode()).digest()
socket_client.send(password_hash)

response = socket_client.recv(4)
if response != b"OK": 
    print("❌ Błędne hasło. Zamykam sesje")
    socket_client.close()
    quit()

try:
    while True:
        pathname = input("Podaj nazwę lub ścieżkę pliku do wysłania: ").strip()
        if pathname.lower() == 'exit':
            print("Koniec wysyłania pliku.")
            break
        if not os.path.isfile(pathname):
            print("Plik nie istnieje. Spróbuj ponownie.")
            continue

        # sprawdzenie formatu rozszerzenia
        filename = os.path.basename(pathname)
        ext = os.path.splitext(filename)[1]
        ext = ext.lower().lstrip('.')

        if ext not in ALLOWED_EXT:
            print(f"Format *.{ext} nie jest obsługiwany. Dozwolone rozszerzenia: {ALLOWED_EXT}")
            continue
        socket_client.send(filename.encode())

        filesize = os.path.getsize(pathname)

        if filesize > MAX_SIZE:
            print("Plik jest za duży. Maksymalny rozmiar to 10MiB")
            continue
        
        #wysyłanie rozmiaru pliku do serwera
        print(f"Wysyłanie danych...{filesize}")
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
