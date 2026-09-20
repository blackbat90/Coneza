import subprocess
import sys

def run_remote(cmd: str):
    full_cmd = ["ssh", "-n", "root@195.90.215.204", cmd]
    res = subprocess.run(full_cmd, capture_output=True, text=True, encoding="utf-8")
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    return res.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(run_remote(sys.argv[1]))
    else:
        print("Usage: python remote_exec.py '<command>'")
