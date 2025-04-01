import asyncio
import websockets
import socket

# Konfigurasi WebSocket Reverse
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 443  # Port WebSocket
FORWARD_HOST = "8.215.192.205"  # IP server tujuan (misal, SSH lokal)
FORWARD_PORT = 22  # Port SSH

# Bug host dan payload
BUG_HOST = "dev.appsflyer.com"  # Ganti dengan bug yang bekerja
PAYLOAD = f"GET / HTTP/1.1\r\nHost: {BUG_HOST}\r\nUpgrade: websocket\r\nConnection: keep-alive\r\n\r\n"

async def handle_client(websocket, path):
    try:
        print(f"[+] Koneksi dari {websocket.remote_address}")

        # Buat koneksi ke server tujuan (misal, SSH)
        reader, writer = await asyncio.open_connection(FORWARD_HOST, FORWARD_PORT)

        # Kirim payload untuk menyamarkan koneksi
        writer.write(PAYLOAD.encode())
        await writer.drain()

        async def client_to_server():
            async for message in websocket:
                writer.write(message.encode())
                await writer.drain()

        async def server_to_client():
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                await websocket.send(data.decode())

        await asyncio.gather(client_to_server(), server_to_client())

    except Exception as e:
        print(f"[-] Error: {e}")

async def main():
    server = await websockets.serve(handle_client, LISTEN_HOST, LISTEN_PORT)
    print(f"[*] WebSocket server berjalan di {LISTEN_HOST}:{LISTEN_PORT}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
