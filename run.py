import sys
import socket
import uvicorn

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def get_local_ip():
    """Finds the local IP of the machine on the Wi-Fi or LAN network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address (does not actually send packets)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8000

    print("=" * 66)
    print("⚡ Starting WeatherGPT Server: Conversational Meteorological AI")
    print(f"💻 Local Computer:  http://localhost:{port}")
    print(f"📱 On Your Phone:    http://{local_ip}:{port}")
    print(f"📡 Real-time WS:     ws://{local_ip}:{port}/ws/alerts")
    print("=" * 66)
    print(f"👉 Make sure your phone and PC are connected to the SAME Wi-Fi or Hotspot!")
    print("=" * 66)

    # Listen on 0.0.0.0 so all network devices (including phones) can access
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
