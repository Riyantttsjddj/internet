
import asyncio
import websockets
import socket

# Konfigurasi WebSocket Reverse
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 80  # Port WebSocket yang menggunakan port 80
FORWARD_HOST = "8.215.192.205"  # IP server tujuan (misal, SSH lokal)
FORWARD_PORT = 22  # Port SSH

# Bug host dan payload
BUG_HOST = "dev.appsflyer.com"  # Ganti dengan bug yang bekerja
PAYLOAD = f"GET / HTTP/1.1\r\nHost: {BUG_HOST}\r\nUpgrade: websocket\r\nConnection: keep-alive\r\n\r\n"

async def handle_client(websocket, path):
    try:
        print(f"[+] Koneksi dari {websocket.remote_address}")

        # Buat koneksi ke server tujuan (misal, SSH)
        remote_socket = socket.create_connection((FORWARD_HOST, FORWARD_PORT))
        
        # Kirim payload untuk menyamarkan koneksi
        remote_socket.sendall(PAYLOAD.encode())

        async def client_to_server():
            async for message in websocket:
                remote_socket.sendall(message.encode())

        async def server_to_client():
            while True:
                data = remote_socket.recv(1024)
                if not data:
                    break
                await websocket.send(data)

        await asyncio.gather(client_to_server(), server_to_client())

    except Exception as e:
        print(f"[-] Error: {e}")

# Jalankan server WebSocket Reverse
start_server = websockets.serve(handle_client, LISTEN_HOST, LISTEN_PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
