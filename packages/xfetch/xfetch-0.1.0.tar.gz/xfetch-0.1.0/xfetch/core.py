# xfetch/core.py
import platform
import socket
import getpass
import psutil
import GPUtil
import datetime

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    return gpus[0].name if gpus else "N/A"

def get_uptime():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    uptime = now - boot_time
    return str(uptime).split('.')[0]

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_system_info():
    username = getpass.getuser()
    hostname = socket.gethostname()
    os_name = platform.system()
    os_version = platform.version()
    release = platform.release()
    arch = platform.machine()
    processor = platform.processor()
    uptime = get_uptime()
    cpu_usage = psutil.cpu_percent(interval=1)
    total_ram = get_size(psutil.virtual_memory().total)
    used_ram = get_size(psutil.virtual_memory().used)
    ram_percent = psutil.virtual_memory().percent
    gpu = get_gpu_info()
    ip_address = socket.gethostbyname(hostname)
    disks = []

    for d in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(d.mountpoint)
            disks.append({
                'device': d.device,
                'mountpoint': d.mountpoint,
                'used': get_size(usage.used),
                'total': get_size(usage.total),
                'percent': usage.percent
            })
        except PermissionError:
            continue

    return {
        'username': username,
        'hostname': hostname,
        'os': f"{os_name} {release} ({os_version})",
        'arch': arch,
        'cpu': processor,
        'gpu': gpu,
        'ram': f"{used_ram} / {total_ram} ({ram_percent}%)",
        'uptime': uptime,
        'cpu_usage': f"{cpu_usage}%",
        'ip': ip_address,
        'disks': disks
    }
