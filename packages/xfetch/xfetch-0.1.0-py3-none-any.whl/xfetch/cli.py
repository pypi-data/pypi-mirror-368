# xfetch/cli.py
from .core import get_system_info

def print_info():
    info = get_system_info()

    print(f"""
\x1b[1mUser:     \x1b[0m{info['username']}
\x1b[1mHost:     \x1b[0m{info['hostname']}
\x1b[1mOS:       \x1b[0m{info['os']}
\x1b[1mArch:     \x1b[0m{info['arch']}
\x1b[1mCPU:      \x1b[0m{info['cpu']}
\x1b[1mGPU:      \x1b[0m{info['gpu']}
\x1b[1mRAM:      \x1b[0m{info['ram']}
\x1b[1mUptime:   \x1b[0m{info['uptime']}
\x1b[1mCPU Load: \x1b[0m{info['cpu_usage']}
\x1b[1mIP Addr:  \x1b[0m{info['ip']}
""")

    print("\x1b[1mDisks:\x1b[0m")
    for d in info['disks']:
        print(f"  {d['device']} - {d['mountpoint']}: {d['used']} / {d['total']} ({d['percent']}%)")

if __name__ == "__main__":
    print_info()
