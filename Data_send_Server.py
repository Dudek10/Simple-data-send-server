import socket
import threading
import struct
import os
import hashlib
import time

HOST = '127.0.0.1'
PORT = 5000


def handle_client(client_socket, client_address, password, MAX_SIZE, hash_file):
    try:
        # Odbiór hasła
        password_hash = client_socket.recv(32)
        if password_hash == b'':
            print(f"Klient {client_address} nie podał hasła.")
            client_socket.close()
            return

        if not os.path.exists(hash_file):
            with open(hash_file, 'wb') as f:
                f.write(password)
                print("🔐 Nowe hasło zapisane pomyślnie")
        else:
            with open(hash_file, 'rb') as f:
                server_hash = f.read()
                if password_hash != password:
                    print(f" Hasło nie jest zgodne. Zamykam połączenie z {client_address}")
                    client_socket.close()
                    if client_socket in unauthorized_clients:
                        unauthorized_clients.remove(client_socket)
                    return
                else:
                    client_socket.send(b"OK")
                    print("✅ Hasło poprawne.")
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
            if file_size > MAX_SIZE:
                print("❌ Plik jest za duży (maks. 10MB)")
                continue

            print(f"📁 Otrzymano plik: {filename} o rozmiarze {file_size} bajtów")

            received = 0
            filename = os.path.basename(filename) # automatyczny zapis do folderu 'received'
            filepath = os.path.join("received", filename)

            # Sprawdzenie formatu rozszerzenia
            _, ext = os.path.splitext(filename)
            ext = ext.lower().lstrip('.')
            if ext not in allowed_extensions:
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
                    print(f"pobieranie danych...{chunk_size}")

            print(f"✅ Plik {filename} zapisany.")

    except Exception as e:
        print(f"Błąd podczas obsługi klienta {client_address}: {e}")

    # Zakończenie programu
    finally:
        client_socket.close()
        print(f"Połączenie z {client_address} zakończone.")

        if client_socket in authorized_clients:
            authorized_clients.remove(client_socket)
        if client_socket in unauthorized_clients:
            unauthorized_clients.remove(client_socket)


#stworzenie nowego folderu do przechowywania odebranych plików
if not os.path.exists("received"):
    os.makedirs("received", exist_ok=True)

allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'txt'}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"🟢 Serwer działa na http://{HOST}:{PORT}")

# lista do przechowywania nieautoryzowanych i autoryzowanych klientów
unauthorized_clients = []
authorized_clients = []

server_password = input(" Utwórz hasło: ").strip()
password = hashlib.sha512(server_password.encode()).digest()

hash_file = "server_hash.txt"
MAX_SIZE = 10485760

# Oczekiwanie na połączenie z nowym klientem
while True:
    client_socket, client_address = server_socket.accept()
    unauthorized_clients.append(client_socket)
    print(f"🔗 Połączono z {client_address}")
    threading.Thread(target=handle_client, args=(client_socket, client_address, password, MAX_SIZE, hash_file)).start()
