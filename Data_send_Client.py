import time
import socket
import os
import struct
import hashlib

HOST = '127.0.0.1'
PORT = 5000
MAX_SIZE = 10485760
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif', 'txt'}

def recv_until_newline(sock):
    data = b""
    while not data.endswith(b"\n"):
        part = sock.recv(1024)
        if not part:
            break
        data += part
    return data.strip()

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect((HOST, PORT))

i = 0
while i < 3:
    password = input("🔑 Podaj hasło dostępu: ").strip()
    password_hash = hashlib.sha512(password.encode()).digest()
    socket_client.send(password_hash)
    response = socket_client.recv(32)
    if response == b"OK":
        print("✅ Hasło poprawne.\n")
        break
    elif response == b'PASSWORD_NOT_PROVIDED':
        print("Klient nie podał hasła.\n")
        time.sleep(3)
        socket_client.close()
        quit()
    elif response == b'WRONG_PASSWORD':
        print("❌ Błędne hasło. Spróbuj ponownie.\n")
        i += 1
    if i == 3:
        print("Zbyt wiele prób wpisania hasła! Kończę sesję")
        time.sleep(3)
        socket_client.close()
        quit()
    
try:
    while True:
        pathname = input("Podaj Nazwę *..\\NazwaPliku* lub  bezwzględną ścieżkę pliku do wysłania *C:\\...* (exit by wyjść): ").strip()
        if pathname.lower() == 'exit':
            print("Koniec wysyłania pliku.")
            break
        if not os.path.isfile(pathname):
            print("Plik nie istnieje. Spróbuj ponownie.\n")
            continue

        # sprawdzenie formatu rozszerzenia
        filename = os.path.basename(pathname)
        ext = os.path.splitext(filename)[1]
        ext = ext.lower().lstrip('.')

        if ext not in ALLOWED_EXT:
            print(f"Format *.{ext} nie jest obsługiwany. Dozwolone rozszerzenia: {ALLOWED_EXT}\n")
            continue
        socket_client.send(filename.encode())

        filesize = os.path.getsize(pathname)

        if filesize > MAX_SIZE:
            print("Plik jest za duży. Maksymalny rozmiar to 10MiB.\n")
            continue
        
        #wysyłanie rozmiaru pliku do serwera
        print(f"Wysyłanie danych... {filesize}B.")

        socket_client.send(struct.pack('!Q', filesize))

        with open(pathname, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                socket_client.send(data)
            
            DATA = recv_until_newline(socket_client)
            if DATA == b"File_received":
                print(f"✅ Plik {filename} został wysłany.\n")
            else:
                print("❌ Błąd podczas wysyłania pliku.\n")
            continue
finally:
    socket_client.close()
