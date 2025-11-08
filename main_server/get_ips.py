import Thread

def scan_lan(network="10.29.60.0/24"):
    global online_ips_cache
    while True:
        net = ipaddress.ip_network(network, strict=False)
        temp_online = []
        for ip in net.hosts():
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)],
                                    stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                temp_online.append(str(ip))
        online_ips_cache = temp_online
        # wait 30 seconds before next scan
        time.sleep(30)

# Start LAN scanning in a separate thread
threading.Thread(target=scan_lan, daemon=True).start()
