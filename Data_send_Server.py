
import socket
import threading
import struct
import os
import hashlib
import time

HOST = '127.0.0.1'
PORT = 5000
MAX_SIZE = 10485760
HASH_FILE = "server_hash.txt"
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif', 'txt'}


def handle_client(client_socket, client_address, password, max_size, hash_file):
    try:
        # Odbiór hasła
        password_hash = client_socket.recv(64)
        if password_hash == b'':
            print(f"Klient {client_address} nie podał hasła.")
            client_socket.send(b"PASSWORD_NOT_PROVIDED")
            client_socket.close()
            return
        else:
            if password_hash != password:
                print(f"Hasło nie jest zgodne u klienta: {client_address}")
                return
            else:
                client_socket.send(b"OK")
                print(f"✅ Klient: {client_address} wpisał poprawne Hasło")
                if client_socket not in authorized_clients:
                    unauthorized_clients.remove(client_socket)
                    authorized_clients.append(client_socket)
        while True:
            # Odbiór rozmiaru i nazwy pliku
            filename_bytes = client_socket.recv(1024)
            if not filename_bytes:
                print(f"Klient {client_address} rozłączył się.")
                break
            filename = filename_bytes.decode()

            length_bytes = client_socket.recv(8)
            if not length_bytes:
                print(f"Klient {client_address} rozłączył się podczas odbioru rozmiaru pliku.")
                break

            file_size = struct.unpack('!Q', length_bytes)[0] 
            if file_size > max_size:
                print("❌ Plik jest za duży (maks. 10MB)")
                continue

            print(f"📁 Otrzymano plik: {filename} o rozmiarze {file_size} bajtów")

            received = 0
            filename = os.path.basename(filename) # automatyczny zapis do folderu 'received'
            filepath = os.path.join("received", filename)

            # Sprawdzenie formatu rozszerzenia
            _, ext = os.path.splitext(filename)
            ext = ext.lower().lstrip('.')
            if ext not in ALLOWED_EXT:
                print(f"Klient podaj zły format: {ext}")
                continue

            #wysyłanie dokładnego rozmiaru pliku
            with open(filepath, 'wb') as f:
                while received < file_size:
                    chunk_size = min(1024, file_size - received)
                    data = client_socket.recv(chunk_size)
                    if not data:
                        print(f"Połączenie przerwane podczas odbioru pliku {filename}")
                        break
                    f.write(data)
                    received += len(data)

                for i in range(3):
                    time.sleep(2)
                    print(f"Pobieranie danych...{received / file_size}")

            print(f"✅ Plik {filename} zapisany.")
            #Wysylanie wiadomosci o zakończeniu pobierania
            client_socket.send(b"File_received\n")

    except Exception as e:
        print(f"Błąd podczas obsługi klienta {client_address}: {e}")

    # Zakończenie programu
    finally:
        client_socket.close()
        print(f"Połączenie z {client_address} zakończone.")

        if client_socket in authorized_clients:
            authorized_clients.remove(client_socket)
        elif client_socket in unauthorized_clients:
            unauthorized_clients.remove(client_socket)


if not os.path.exists(HASH_FILE):
    password = input("Utwórz hasło: ").strip()
    password_hash = hashlib.sha512(password.encode()).digest()

    with open(HASH_FILE, 'wb') as f:
        f.write(password_hash)
        print("🔐 Nowe hasło zapisane pomyślnie")
else:
    with open(HASH_FILE, 'rb') as f:
        password_hash = f.read()

#stworzenie nowego folderu do przechowywania odebranych plików
if not os.path.exists("received"):
    os.makedirs("received", exist_ok=True)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"🟢 Serwer działa na http://{HOST}:{PORT}")

# lista do przechowywania nieautoryzowanych i autoryzowanych klientów
unauthorized_clients = []
authorized_clients = []

# Oczekiwanie na połączenie z nowym klientem
while True:
    client_socket, client_address = server_socket.accept()
    unauthorized_clients.append(client_socket)
    print(f"🔗 Połączono z {client_address}")
    threading.Thread(target=handle_client, args=(client_socket, client_address, password_hash, MAX_SIZE, HASH_FILE)).start()
