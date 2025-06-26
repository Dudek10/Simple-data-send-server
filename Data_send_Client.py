import socket
import os
import struct
import hashlib

HOST = '127.0.0.1'
PORT = 5000

allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'txt'}

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect((HOST, PORT))


try:
    while True:
        password = input("🔑 Podaj hasło dostępu: ").strip()
        password_hash = hashlib.sha256(password.encode()).digest()
        socket_client.send(password_hash)

        response = socket_client.recv(4)
        if response != b"OK": 
            print("❌ Błędne hasło. Zamykam sesje")
            break

        pathname = input("Podaj nazwę lub ścieżkę pliku do wysłania: ").strip()
        if pathname.lower() == 'exit':
            print("Koniec wysyłania pliku.")
            break
        if not os.path.isfile(pathname):
            print("Plik nie istnieje. Spróbuj ponownie.")
            continue

        # sprawdzenie formatu rozszerzenia
        filename = os.path.basename(pathname)
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip('.')

        if ext not in allowed_extensions:
            print(f"Format .{ext} nie jest obsługiwany. dozwolone rozszerzenia: {allowed_extensions}")
            continue
        socket_client.send(filename.encode())

        #wysyłanie rozmiaru pliku do serwera
        filesize = os.path.getsize(pathname)
        time.sleep(2)
        print(f"wysyłanie danych...{filesize}")
        time.sleep(2)
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
