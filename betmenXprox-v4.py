import os
import sys
import httpx
import re
from colorama import Fore, init
import threading
from queue import Queue
import time
from enum import Enum
import fcntl
import atexit
import psutil
import datetime
import subprocess

init(autoreset=True)

fr = Fore.RED
fg = Fore.GREEN
fy = Fore.YELLOW
fw = Fore.WHITE
fb = Fore.BLUE
fm = Fore.MAGENTA
fre = Fore.RESET

# Define the lock file path
LOCK_FILE = '/tmp/proxy_script.lock'
PID_FILE = '/tmp/proxy_script.pid'

def check_command(command):
    """Check if a command is available"""
    try:
        subprocess.run(['which', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def print_banner():
    """Print the banner using figlet and lolcat"""
    try:
        # Check if figlet and lolcat are installed
        if not all(check_command(cmd) for cmd in ['figlet', 'lolcat']):
            print(f"{fr}Please install figlet and lolcat first:{fre}")
            print("sudo apt-get install figlet lolcat")
            sys.exit(1)

        # Print the main banner
        os.system('figlet -f big "BETMEN" | lolcat -a -d 1')
        os.system('figlet -f small "Nyari Proxy" | lolcat -a -d 1')
        
        # Print description with colorama
        print(f"\n{fg}╔══════════════════════════════════════════════════════════╗{fre}")
        print(f"{fg}║{fy}             Proxy Hunter and Checker Tool              {fg}║{fre}")
        print(f"{fg}║{fw}   Nyari proxy sambil buka winbox cess - adakah 100     {fg}║{fre}")
        print(f"{fg}║{fb} di bikin bareng AI - mumet klo sndiri cuy - tojenga    {fg}║{fre}")
        print(f"{fg}╚══════════════════════════════════════════════════════════╝{fre}")
        print(f"\n{fm}[*] Starting proxy collection and verification...{fre}\n")
    except Exception as e:
        print(f"{fr}Error printing banner: {e}{fre}")

class ProcessLock:
    def __init__(self, lock_file):
        self.lock_file = lock_file
        self.lock_fd = None

    def acquire(self):
        try:
            # Open the lock file
            self.lock_fd = open(self.lock_file, 'w')
            
            # Try to acquire an exclusive lock
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write current PID to lock file
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
            
            return True
        except (IOError, OSError):
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            return False

    def release(self):
        if self.lock_fd:
            fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            self.lock_fd.close()
            try:
                os.remove(self.lock_file)
            except OSError:
                pass

def check_running_instance():
    """
    Check if another instance is running and get its details
    Returns: (is_running, runtime_minutes, pid)
    """
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
                process = psutil.Process(pid)
                
                # Get process start time
                start_time = datetime.datetime.fromtimestamp(process.create_time())
                current_time = datetime.datetime.now()
                runtime = current_time - start_time
                
                return True, runtime.total_seconds() / 60, pid
        except (ProcessLookupError, psutil.NoSuchProcess, ValueError):
            # Process no longer exists
            os.remove(PID_FILE)
    return False, 0, None

def write_pid():
    """Write current process ID to PID file"""
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def cleanup():
    """Cleanup function to remove PID file on exit"""
    try:
        os.remove(PID_FILE)
    except OSError:
        pass

# Register cleanup function
atexit.register(cleanup)

class ProxyType(Enum):
    HTTP = "http"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

# Add SOCKS proxy sources
proxy_sources = {
    ProxyType.HTTP: [
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt',
        'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt',
        'https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
        'https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt',
        'https://raw.githubusercontent.com/yuceltoluyag/GoodProxy/main/raw.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
        'https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt',
        'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt',
        'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt',
        'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt',
        'https://api.openproxylist.xyz/http.txt',
        'https://api.proxyscrape.com/v2/?request=displayproxies',
        'https://api.proxyscrape.com/?request=displayproxies&proxytype=http',
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        'https://www.proxydocker.com/en/proxylist/download?email=noshare&country=all&city=all&port=all&type=all&anonymity=all&state=all&need=all',
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=anonymous',
        'http://worm.rip/http.txt',
        'https://proxyspace.pro/http.txt',
        'https://multiproxy.org/txt_all/proxy.txt',
        'https://proxy-spider.com/api/proxies.example.txt',
        'https://raw.githubusercontent.com/sunny9577/proxy-scraper/refs/heads/master/proxies.txt',
        'https://raw.githubusercontent.com/ALIILAPRO/Proxy/refs/heads/main/http.txt',
        'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
        'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt',
        'https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/free.txt',
        'https://raw.githubusercontent.com/TuanMinPay/live-proxy/refs/heads/master/http.txt',
        'https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt',
        'https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt',
        'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt',
        'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt',
        'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt',
        'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/refs/heads/master/http.txt',
        'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/refs/heads/master/https.txt',
        'https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/refs/heads/main/proxies/all.txt',
        'https://raw.githubusercontent.com/azis-alvriyanto/fresh-proxy-list/archive/storage/classic/http.txt',
        'https://raw.githubusercontent.com/azis-alvriyanto/fresh-proxy-list/archive/storage/classic/https.txt',
    ],
    ProxyType.SOCKS4: [
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
        'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt',
        'https://www.proxy-list.download/api/v1/get?type=socks4',
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4',
        'https://proxyspace.pro/socks4.txt',
        'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt',
    ],
    ProxyType.SOCKS5: [
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
        'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt',
        'https://www.proxy-list.download/api/v1/get?type=socks5',
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5',
        'https://proxyspace.pro/socks5.txt',
        'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt',
    ]
}

def normalize_proxy(proxy_line):
    """
    Normalize different proxy patterns to ip:port format and detect proxy type.
    Returns tuple (normalized_proxy, proxy_type) or (None, None) if invalid.
    """
    proxy_line = proxy_line.strip().lower()
    
    if not proxy_line:
        return None, None
        
    patterns = [
        # Standard ip:port
        r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$',
        # ip:port:type/country/other_info
        r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+):[^:]*$',
        # protocol://ip:port
        r'^(?:https?|socks4|socks5)?://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
        # username:password@ip:port
        r'^.*?@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, proxy_line)
        if match:
            ip, port = match.groups()
            try:
                octets = [int(x) for x in ip.split('.')]
                if all(0 <= octet <= 255 for octet in octets):
                    port_num = int(port)
                    if 1 <= port_num <= 65535:
                        return f"{ip}:{port}", None
            except ValueError:
                continue
    
    return None, None

def clean_old_files(files):
    """Clean up old files before starting new download"""
    for file in files:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"{fy}Removed old {file}{fre}")
                time.sleep(0.1)
        except Exception as e:
            print(f"{fr}Error removing {file}: {e}{fre}")
            sys.exit(1)

def download_proxies():
    try:
        # Clean up old files first
        files_to_clean = ['http.txt', 'socks4.txt', 'socks5.txt']
        clean_old_files(files_to_clean)
        print(f"{fy}Starting download of new proxies...{fre}\n")

        proxy_counts = {proxy_type: 0 for proxy_type in ProxyType}
        
        for proxy_type, sources in proxy_sources.items():
            normalized_proxies = set()
            
            for proxy_url in sources:
                try:
                    response = httpx.get(proxy_url, timeout=10)
                    if response.status_code == 200:
                        for line in response.text.splitlines():
                            normalized, _ = normalize_proxy(line)
                            if normalized:
                                normalized_proxies.add(normalized)
                        print(f" -| Retrieved {fg}{proxy_url}")
                    else:
                        print(f" -| Failed to retrieve {fr}{proxy_url} (Status code: {response.status_code})")
                except Exception as e:
                    print(f" -| Error retrieving {fr}{proxy_url}: {e}")

            # Write normalized proxies to corresponding file
            if normalized_proxies:
                filename = f"{proxy_type.value}.txt"
                with open(filename, 'w') as f:
                    for proxy in sorted(normalized_proxies):
                        f.write(proxy + '\n')
                proxy_counts[proxy_type] = len(normalized_proxies)
                print(f"\n{fw}( {fy}{len(normalized_proxies)} {fw}) {fg}{proxy_type.value.upper()} proxies saved to {filename}")

        return proxy_counts

    except Exception as e:
        print(f"{fr}An error occurred during proxy download: {e}")
        sys.exit(1)

def check_proxy(proxy, proxy_type, live_proxies, file_lock):
    try:
        if proxy_type == ProxyType.HTTP:
            proxies = {
                'http://': f'http://{proxy}',
                'https://': f'http://{proxy}',
            }
        else:
            proxies = {
                'http://': f'{proxy_type.value}://{proxy}',
                'https://': f'{proxy_type.value}://{proxy}',
            }
            
        response = httpx.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"{fg}[LIVE]{fre} ({proxy_type.value}) {proxy}")
            with file_lock:
                with open(f'valid.{proxy_type.value}.txt', 'a') as f:
                    f.write(proxy + '\n')
                    f.flush()
            live_proxies.append(proxy)
        else:
            print(f"{fr}[DEAD]{fre} ({proxy_type.value}) {proxy}")
    except Exception:
        print(f"{fr}[DEAD]{fre} ({proxy_type.value}) {proxy}")

def worker(queue, live_proxies, file_lock):
    while True:
        item = queue.get()
        if item is None:
            break
        proxy, proxy_type = item
        check_proxy(proxy, proxy_type, live_proxies, file_lock)
        queue.task_done()

def check_proxies():
    print(f"\n{fy}Checking proxies...\n")
    live_proxies = []
    
    queue = Queue()
    num_threads = 100
    threads = []
    file_lock = threading.Lock()

    # Clean up old valid proxy files
    clean_old_files(['valid.http.txt', 'valid.socks4.txt', 'valid.socks5.txt'])

    # Start worker threads
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(queue, live_proxies, file_lock))
        t.daemon = True
        t.start()
        threads.append(t)

    # Queue proxies for checking
    for proxy_type in ProxyType:
        filename = f"{proxy_type.value}.txt"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                proxies = set(line.strip() for line in f if line.strip())
                for proxy in proxies:
                    queue.put((proxy, proxy_type))

    queue.join()

    # Stop workers
    for _ in range(num_threads):
        queue.put(None)
    for t in threads:
        t.join()

    print(f"\n{fw}Proxy checking completed. Check valid.*.txt files for results.")

def main():
    # Check for running instance
    is_running, runtime_minutes, pid = check_running_instance()
    if is_running:
        print(f"{fr}Another instance (PID: {pid}) is already running for {runtime_minutes:.1f} minutes")
        print(f"{fy}Skipping this run. Will try again in the next scheduled time.{fre}")
        sys.exit(1)

    # Create process lock
    lock = ProcessLock(LOCK_FILE)
    if not lock.acquire():
        print(f"{fr}Another instance is already running. Exiting.{fre}")
        sys.exit(1)

    try:
        # Write PID file
        write_pid()

        # Print the banner
        print_banner()

        # Log start time
        start_time = datetime.datetime.now()
        print(f"{fg}Started proxy collection at {start_time.strftime('%Y-%m-%d %H:%M:%S')}{fre}")

        # Your existing main logic
        proxy_counts = download_proxies()
        print(f"\n{fy}Summary of downloaded proxies:{fre}")
        for proxy_type, count in proxy_counts.items():
            print(f"{fw}- {proxy_type.value.upper()}: {fg}{count} {fw}proxies")
        
        check_proxies()

        # Log completion time and duration
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        print(f"\n{fg}Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total runtime: {duration:.1f} minutes{fre}")

    except Exception as e:
        print(f"{fr}An error occurred: {e}{fre}")
        raise
    finally:
        # Release lock and cleanup
        lock.release()

if __name__ == "__main__":
    main()        
   
