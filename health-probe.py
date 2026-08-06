#!/usr/bin/env python3
"""Free-Stack HQ health probe — pings every wired free endpoint, writes health.json
for the HQ dashboard. No values printed, status only."""
import json, os, subprocess

OUT = r'C:\Users\margo\.easyclaw\workspace\free-stack-hq\health.json'

def vault(name):
    r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', r'C:\Users\margo\.easyclaw\workspace\scripts\vault.ps1',
        '-Action', 'get', '-Name', name], capture_output=True, text=True, timeout=90)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''

def groq_key():
    import yaml as _y
    try:
        c = _y.safe_load(open(r'C:/Users/margo/AppData/Local/hermes/config.yaml', encoding='utf-8'))
        return (c.get('providers') or {}).get('groq', {}).get('api_key', '')
    except Exception:
        return ''

def env(key):
    for line in open(r'C:\Users\margo\AppData\Local\hermes\.env', encoding='utf-8', errors='ignore'):
        if line.startswith(key + '='):
            return line.split('=', 1)[1].strip().strip('\r')
    return ''

def ping(name, method, url, key, payload=None, timeout=25):
    cmd = ['curl', '-s', '-o', '/dev/null', '-m', str(timeout), '-w', '%{http_code}',
           '-X', method, '-H', f'Authorization: Bearer {key}', '-H', 'Content-Type: application/json']
    if payload:
        cmd += ['-d', json.dumps(payload)]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        return r.stdout.strip() or 'ERR'
    except Exception as e:
        return 'ERR'

results = {}
def probe(name, method, url, key, payload=None):
    results[name] = 'NO-KEY' if not key else ping(name, method, url, key, payload)

probe('puter', 'POST', 'https://api.puter.com/puterai/openai/v1/chat/completions', vault('puter'),
      {'model': 'claude-opus-4.7', 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 3})
probe('sambanova', 'POST', 'https://api.sambanova.ai/v1/chat/completions', vault('sambanova'),
      {'model': 'Meta-Llama-3.3-70B-Instruct', 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 3})
probe('cerebras', 'GET', 'https://api.cerebras.ai/v1/models', vault('cerebras'))
probe('deepseek', 'POST', 'https://api.deepseek.com/v1/chat/completions', env('DEEPSEEK_API_KEY'),
      {'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 3})
probe('groq', 'GET', 'https://api.groq.com/openai/v1/models', groq_key())
probe('nvidia', 'GET', 'https://integrate.api.nvidia.com/v1/models', env('KIMI_CN_API_KEY').replace('Bearer ', ''))
probe('huggingface', 'GET', 'https://huggingface.co/api/whoami-v2', vault('huggingface'))
probe('assemblyai', 'GET', 'https://api.assemblyai.com/v2/account', vault('assemblyai'))
probe('deepgram', 'GET', 'https://api.deepgram.com/v1/auth/keys', vault('deepgram'))
probe('cloudflare-aigw', 'GET', 'https://api.cloudflare.com/client/v4/user/tokens/verify', vault('cloudflare-aigateway'))
probe('nebius', 'GET', 'https://api.nebius.ai/v1/models', vault('nebius'))
probe('opencodezen', 'GET', 'https://api.opencodezen.ai/v1/models', vault('opencodezen'))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({'checked_at': __import__('datetime').datetime.now().isoformat(), 'providers': results},
          open(OUT, 'w'), indent=2)
for k, v in results.items():
    print(f'{k}: {v}')
