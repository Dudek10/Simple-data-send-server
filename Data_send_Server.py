import socket
import threading
import struct
import os

if not os.path.exists("received"):
    os.makedirs("received", exist_ok=True)

HOST = '192.168.0.15'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"🟢 Serwer działa na http://{HOST}:{PORT}")
clients = []

def handle_client(client_socket, client_address):
    try:
        while True:
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

            print(f"📁 Otrzymano plik: {filename} o rozmiarze {file_size} bajtów")

            received = 0
            filename = os.path.basename(filename) # automatyczny zapis do folderu 'received'
            filepath = os.path.join("received", filename)
            with open(filepath, 'wb') as f:
                while received < file_size:
                    chunk_size = min(1024, file_size - received)
                    data = client_socket.recv(chunk_size)
                    if not data:
                        print(f"Połączenie przerwane podczas odbioru pliku {filename}")
                        break
                    f.write(data)
                    received += len(data)

            print(f"✅ Plik {filename} zapisany.")

    except Exception as e:
        print(f"Błąd podczas obsługi klienta {client_address}: {e}")

    finally:
        client_socket.close()
        print(f"Połączenie z {client_address} zakończone.")
while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    print(f"🔗 Połączono z {client_address}")
    threading.Thread(target=handle_client, args=(client_socket, client_address)).start()