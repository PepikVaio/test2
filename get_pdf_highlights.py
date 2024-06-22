import os
import paramiko
import json

# Nastavení zařízení
USERNAME = os.getenv('USERNAME')
HOST = os.getenv('HOST')
PASS = os.getenv('PASS')
PATH_XOCHITL = "/home/root/.local/share/remarkable/xochitl/"

# Funkce pro připojení k zařízení Remarkable pomocí SSH
def ssh_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USERNAME, password=PASS)
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode()
    ssh.close()
    return result

# Získání seznamu všech zvýrazněných souborů
print("Přihlašuji se k zařízení pro získání seznamu všech zvýrazněných souborů (PDF i ostatní)")
files_highlighted = ssh_command(f"cd {PATH_XOCHITL} && ls -1d *.highlights").splitlines()

# Filtrujeme pouze PDF soubory
pdf_highlights = []
for highlight in files_highlighted:
    bare_name = highlight.replace(".highlights", "")
    content_name = f"{bare_name}.content"
    content = ssh_command(f"grep -q 'pdf' {PATH_XOCHITL}{content_name} && cat {PATH_XOCHITL}{content_name}")
    if content:
        pdf_highlights.append(content_name)

results = []
for content_file in pdf_highlights:
    bare_name = content_file.replace(".content", "")
    pages = json.loads(ssh_command(f"cat {PATH_XOCHITL}{content_file}"))["pages"]

    for page_id in pages:
        json_file = f"{PATH_XOCHITL}{bare_name}.highlights/{page_id}.json"
        if json.loads(ssh_command(f"test -f {json_file} && cat {json_file}")):
            highlights = json.loads(ssh_command(f"cat {json_file}"))["highlights"]
            sorted_highlights = sorted(highlights, key=lambda x: x["start"])
            page_highlights = [highlight["text"] for highlight in sorted_highlights]
            results.append({"page": page_id, "highlights": page_highlights})

print(json.dumps(results, indent=2))
