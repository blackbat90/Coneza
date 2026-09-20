import subprocess

def run_remote(script: str):
    clean = script.replace('\r\n', '\n').strip() + '\n'
    p = subprocess.Popen(
        ['ssh', 'root@195.90.215.204', 'bash -s'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    out, err = p.communicate(input=clean)
    return out, err, p.returncode

def main():
    # Find where the env file lives
    print("=== Inspecting coneza-backend-server ===")
    script = """
docker inspect coneza-backend-server | python3 -c "
import sys, json
d = json.load(sys.stdin)[0]
print('Mounts:')
for m in d.get('Mounts', []):
    print(' ', m.get('Source'), '->', m.get('Destination'))
print('Env (non-secret):')
for e in d['Config']['Env']:
    if 'PASS' not in e.upper() and 'SECRET' not in e.upper() and 'TOKEN' not in e.upper():
        print(' ', e)
print('Labels:')
for k,v in d.get('Config', {}).get('Labels', {}).items():
    print(' ', k, '=', v)
"
"""
    out, err, rc = run_remote(script)
    print(out)
    if err:
        print("ERR:", err[:500])
    
    # Also check docker-compose or env file path
    print("=== Finding docker-compose files ===")
    script2 = """
find /srv/coneza* -name "docker-compose*" -o -name ".env" 2>/dev/null | head -20
ls /srv/ 
"""
    out2, err2, rc2 = run_remote(script2)
    print(out2)

if __name__ == '__main__':
    main()
