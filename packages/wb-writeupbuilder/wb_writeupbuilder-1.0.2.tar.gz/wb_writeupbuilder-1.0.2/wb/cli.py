#!/usr/bin/env python3
import argparse
import sys
import time
import threading
import re
from datetime import datetime
import colorama
from colorama import Back as bg, Fore, Style, init
init(autoreset=True)


try:
    from zoneinfo import ZoneInfo
    BERLIN = ZoneInfo("Europe/Berlin")
except Exception:
    BERLIN = None

# ─────────────────────────────────────────────
# Spinner
def spinner(stop_event, message=""):
    symbols = ["|", "/", "–", "\\"]
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{message} {symbols[idx]} ")
        sys.stdout.flush()
        idx = (idx + 1) % len(symbols)
        time.sleep(0.1)
    # Clear spinner line after stopping
    sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
    sys.stdout.flush()

def spinner_until_enter(message=""):
    """Show spinner with a message until user presses Enter."""
    # Print "(Press Enter...)" below where spinner will run
    sys.stdout.write("\n" + Fore.CYAN + "(Press Enter to continue)" + Style.RESET_ALL + "\n")
    sys.stdout.flush()

    # Move cursor up to start spinner above "(Press Enter...)"
    sys.stdout.write("\033[F\033[F")  # Move up two lines
    sys.stdout.flush()

    # Start spinner with message
    stop_event = threading.Event()
    thread = threading.Thread(target=spinner, args=(stop_event, message))
    thread.start()

    try:
        input()  # Wait for Enter
    finally:
        stop_event.set()
        thread.join()


# ─────────────────────────────────────────────
# Utilities
def sanitize_filename(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s)
    return s.lower() or "untitled"

def today_date_str():
    if BERLIN:
        return datetime.now(BERLIN).strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")

# ─────────────────────────────────────────────
# Input handlers
def prompt_normal(prompt_text: str, required: bool = False) -> str | None:
    while True:
        ans = input(Fore.WHITE + f"{prompt_text}: " + Style.RESET_ALL).strip()
        if ans:
            return ans
        if required:
            print(Fore.RED + "This field is required — please type a value." + Style.RESET_ALL)
            continue
        return None

def prompt_multiline(prompt_text: str) -> str | None:
    print(Fore.WHITE + prompt_text + Style.RESET_ALL)
    print(Fore.CYAN + "(Type `END` on a new line to finish. Press ENTER immediately (empty first line) to skip this question.)" + Style.RESET_ALL)
    first = input()
    if first == "":
        return None
    if first.strip() == "END":
        return None
    lines = [first]
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    content = "\n".join(lines).rstrip()
    return content if content else None

# ─────────────────────────────────────────────
# Markdown builders
def build_overview_md(challenge_name, platform, date_str, solver, category, difficulty, points):
    md = "#  📌 Challenge Overview\n\n"
    md += f"| 🧩 Platform / Event | {platform} |\n"
    md += "| ------------------- | ------------------------------- |\n"
    md += f"| 📅 Date             | {date_str} |\n"
    if solver:
        md += f"| 👾 Solver           | {solver} |\n"
    if category:
        md += f"| 🔰 Category         | {category} |\n"
    if difficulty:
        md += f"| ⭐ Difficulty        | {difficulty} |\n"
    if points:
        md += f"| 🎯 Points           | {points} |\n"
    md += "\n---\n\n"
    return md

def add_section(md, heading, content, inline_template=False):
    if not content:
        return md
    if inline_template:
        md += f"#  🚩 Flag -> `{content}`\n\n---\n\n"
    else:
        md += f"{heading}\n\n{content}\n\n---\n\n"
    return md

# ─────────────────────────────────────────────
# Main writeup builder
def writeup_builder():
    print(f"{Fore.CYAN}Tips for a clean writeup:")
    print(f"\n{bg.BLACK}{Fore.WHITE}- Screenshot as you go through the CTF, then return here to build the writeup.")
    print(f"{bg.BLACK}{Fore.WHITE}- For multi-line sections, press Enter to add new lines, and type `END` on a new line to finish.")
    print(f"{bg.BLACK}{Fore.WHITE}- To insert an image: `![image](imagename.jpg)` — the image file must be in the same directory as the .md file.")
    print(f"{bg.BLACK}{Fore.WHITE}- Skipping: If you press Enter without typing anything, that question will be skipped.")
    print(f"{bg.BLACK}{Fore.WHITE}- Sections with no answers will not be written to the file.{Style.RESET_ALL}\n")

    spinner_until_enter(f"{bg.BLACK}{Fore.GREEN}WriteupBuilder -> Starting")

    print()

    print("# Challenge Overview")
    challenge_name = prompt_normal("Name of the challenge", required=True)
    platform = prompt_normal("Platform / Event", required=True)
    solver = prompt_normal("Who are you (solver)", required=False)
    category = prompt_normal("Category of the challenge", required=False)
    difficulty = prompt_normal("Difficulty of the challenge", required=False)
    points = prompt_normal("Points for solving", required=False)

    date_str = today_date_str()
    filename = f"{sanitize_filename(challenge_name)}-{sanitize_filename(platform)}.md"
    print(f"\n{bg.BLACK}{Fore.WHITE}Writing to file: {filename}{Style.RESET_ALL}\n")

    md = build_overview_md(challenge_name, platform, date_str, solver, category, difficulty, points)

    print("# Initial Info")
    initial_info = prompt_multiline("Paste the challenge description, any attached files, or screenshots here.")
    md = add_section(md, "# 📋 Initial Info:", initial_info)

    print("# Initial Analysis")
    initial_analysis = prompt_multiline("What stood out during your first inspection? Mention suspicious URLs, strange files, unusual behavior, etc.")
    md = add_section(md, "# 🔍 Initial Analysis:", initial_analysis)

    print("# Exploitation")
    exploitation = prompt_multiline("Describe the steps and tools/scripts used to exploit the challenge, Explain how each tool worked and how it helped you get the flag.")
    md = add_section(md, "# ⚙️ Exploitation", exploitation)

    print("# Flag")
    flag = prompt_normal("Enter The Flag", required=False)
    md = add_section(md, "#  🚩 Flag ->", flag, inline_template=True)
    print("\n")
    print("# Takeaways")
    takeaways = prompt_multiline("List the commands, tricks, or concepts you learned from this challenge.")
    md = add_section(md, "#  📚 Takeaways", takeaways)

    md = md.rstrip() + "\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)

    print(Fore.WHITE + f"Done. Saved {filename}" + Style.RESET_ALL)

# ─────────────────────────────────────────────
# Template builder
def template_builder(args):
    spinner_until_enter(f"{bg.BLACK}{Fore.GREEN} WriteupBuilder -> Writing the Advanced Writeup Template to {args.filename}")
    print()

    md = """# 1- Initial Reconnaissance

## Port Scanning  
We start with a full nmap scan to identify exposed services:  
# Quick initial scan
nmap -sS -O -sV -sC -p- --min-rate=1000 -oN initial_scan.txt

# Detailed scan of open ports  
nmap -sV -sC -A -p -oN detailed_scan.txt

# UDP scan (top ports)  
sudo nmap -sU --top-ports 1000 -oN udp_scan.txt

## Service Enumeration  
| Port | Service | Version | Notes |  
|------|---------|---------|-------|  
| 22 | SSH | OpenSSH 7.4 | Banner grabbing |  
| 80 | HTTP | Apache 2.4.6 | Web server |  
| 443 | HTTPS | Apache 2.4.6 | SSL/TLS enabled |

## Web Reconnaissance (if applicable)  
# Discover technologies  
whatweb

# Directory enumeration  
feroxbuster -u http:// -w /usr/share/wordlists/dirb/common.txt

# Alternative: Gobuster  
gobuster dir -u http:// -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

Tools used: nmap, feroxbuster, gobuster, whatweb, nikto


# 2- Web Enumeration

## Initial Analysis  
- Detected technology: [Apache/Nginx/IIS version]  
- CMS/Framework: [WordPress/Drupal/Custom/etc]  
- Backend language: [PHP/Python/Node.js/etc]

## Directory Discovery  
# Main directories found  
feroxbuster -u http:// -w /usr/share/wordlists/dirb/common.txt -x php,html,txt,js

# Subdomains (if applicable)  
gobuster vhost -u -w /usr/share/wordlists/subdomains-top1million-5000.txt

### Interesting Directories:  
- /admin - Admin panel  
- /login - Login form  
- /uploads - Uploads directory  
- /config - Config files

## Vulnerability Analysis  
# Nikto scan  
nikto -h http://

# Burp Suite  
# - Set proxy to 127.0.0.1:8080  
# - Intercept and analyze requests/responses  
# - Look for vulnerable parameters

## Identified Attack Vectors  
- [ ] SQL Injection in login parameters  
- [ ] XSS Stored/Reflected  
- [ ] LFI/RFI in file inclusion  
- [ ] File Upload vulnerabilities  
- [ ] CSRF in critical forms  
- [ ] Directory Traversal

Tools: Burp Suite, Nikto, OWASP ZAP, SQLmap, XSSer


# 3- Exploitation

## Main Attack Vector  
Vulnerability exploited: [SQL Injection / RCE / File Upload / etc]  
Severity: [Critical/High/Medium/Low]  
CVE: [If applicable]

## Exploitation Steps

### 1. Vulnerability Identification  
[Describe how the vulnerability was found]

### 2. Exploit Development  
#!/usr/bin/env python3  
# Exploit for [VULNERABILITY]  
import requests  
import sys

target_url = 'http:///vulnerable_endpoint'  
payload =

def exploit():  
try:  
response = requests.post(target_url, data=payload)  
if 'success_indicator' in response.text:  
print('[+] Exploit successful!')  
print('[+] Response:', response.text)  
else:  
print('[-] Exploit failed')  
except Exception as e:  
print('[-] Error:', e)

if __name__ == '__main__':  
exploit()

### 3. Exploit Execution  
# Run exploit  
python3 exploit.py

# Set up reverse shell (example)  
nc -lvnp 4444 # Listener  
# Payload triggers reverse connection

## Initial Access Obtained  
- User: [www-data / apache / user]  
- Shell type: [bash/sh/cmd]  
- Initial directory: [/var/www/html / /home/user]

## Immediate Post-Exploitation  
# System info  
uname -a  
id  
whoami  
pwd

# Interesting files  
find / -name '*.txt' -type f 2>/dev/null | head -20  
find / -perm -4000 -type f 2>/dev/null # SUID binaries




# 4- Privilege Escalation

## System Enumeration  
# Basic system info  
uname -a  
cat /etc/os-release  
id  
sudo -l

# Running processes  
ps aux | grep root  
ps aux --forest

# Internal services and ports  
netstat -tulpn  
ss -tulpn

## Automated Enumeration Tools  
# LinPEAS (recommended)  
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh

# LinEnum  
./LinEnum.sh

# Linux Exploit Suggester  
./linux-exploit-suggester.sh

## Analyzed Escalation Vectors

### 1. SUID/SGID Binaries  
find / -perm -4000 -type f 2>/dev/null  
find / -perm -2000 -type f 2>/dev/null

# Interesting binaries found:  
# - /usr/bin/[binary_name]  
# - Check GTFOBins for exploitation

### 2. Sudo Misconfigurations  
sudo -l  
# Commands executable as root without password

### 3. Cron Jobs  
cat /etc/crontab  
ls -la /etc/cron.*  
crontab -l

### 4. Kernel Exploits  
# Kernel version  
uname -r

# Applicable exploits:  
# - CVE-XXXX-XXXX: [Description]  
# - Available at: [Exploit URL]

## Successful Escalation  
Method used: [SUID binary / Sudo misconfiguration / Kernel exploit / etc]

# Command/script used to escalate  
[command or specific script]

# Root verification  
id  
whoami  
cat /root/root.txt

Root obtained: ✅





# 5- User Flag

## Flag Location  
File: /home/[username]/user.txt  
Owner user: [username]

## Steps to Obtain the Flag  
# Navigate to user directory  
cd /home/[username]

# Read the flag  
cat user.txt

## User Flag  
[USER_FLAG_HERE]

## Additional Notes  
- The flag was found after [initial shell / partial escalation]  
- File permissions: [ls -la user.txt]  
- Verification hash (if applicable): [md5sum user.txt]

## Screenshot  
[Screenshot showing flag acquisition]




# 6- Root Flag

## Flag Location  
File: /root/root.txt  
Owner user: root  
Permissions: 600 (rw-------)

## Steps to Obtain the Flag  
# Verify root access  
id  
whoami

# Access root directory  
cd /root

# Read the root flag  
cat root.txt

## Root Flag  
[ROOT_FLAG_HERE]

## Full Compromise Verification  
# Verify full system access  
cat /etc/shadow | head -5  
ls -la /root/  
history

## Compromised System Info  
- Hostname: [hostname]  
- Kernel: [uname -r]  
- Distribution: [cat /etc/os-release]  
- Uptime: [uptime]

## Screenshot  
[Screenshot showing root flag acquisition]

---  
🎉 System fully compromised - Root obtained




# 7- Main Vulnerability

## Question  
What was the main vulnerability exploited to gain initial access to the system?

## Answer  
Vulnerability: [Specific vulnerability name]

### Technical Details  
- Type: [SQL Injection / RCE / File Upload / Buffer Overflow / etc]  
- Affected component: [Web app / Service / etc]  
- Vulnerable version: [Specific software version]  
- CVE (if applicable): CVE-XXXX-XXXX  
- CVSS Score: [Score if available]

### Vulnerability Description  
[Detailed explanation of what the vulnerability does and why it is exploitable]

### Impact  
- Confidentiality: [High/Medium/Low]  
- Integrity: [High/Medium/Low]  
- Availability: [High/Medium/Low]

### Attack Vector  
1. [Step 1 of the attack]  
2. [Step 2 of the attack]  
3. [Step 3 of the attack]

### Recommended Mitigation  
- [Mitigation step 1]  
- [Mitigation step 2]  
- [Mitigation step 3]

### References  
- [CVE URL if applicable]  
- [Public exploit URL if used]  
- [Additional documentation]






# 8- Lessons Learned

## CTF Reflections

### 🎯 Key Points  
- [Lesson 1]: [Description of what was learned]  
- [Lesson 2]: [Description of what was learned]  
- [Lesson 3]: [Description of what was learned]

### 💡 Important Techniques  
- Enumeration: [What worked well in recon phase]  
- Exploitation: [Key technique or tool]  
- Escalation: [Method that led to root]

### 🔧 Highlighted Tools  
| Tool | Use | Effectiveness |  
|------|-----|--------------|  
| [Tool 1] | [Purpose] | ⭐⭐⭐⭐⭐ |  
| [Tool 2] | [Purpose] | ⭐⭐⭐⭐ |  
| [Tool 3] | [Purpose] | ⭐⭐⭐ |

### ⚠️ Mistakes Made  
- [Mistake 1]: [What went wrong and how to avoid it]  
- [Mistake 2]: [What went wrong and how to avoid it]

### 📚 New Knowledge  
- [New concept learned 1]  
- [New concept learned 2]  
- [New command/technique discovered]

### 🚀 For Future CTFs  
- [ ] Remember to check [specific file/directory]  
- [ ] Always try [specific technique] in [context]  
- [ ] Never forget to enumerate [specific service/port]  
- [ ] Research more about [technology/concept]

### 📖 Useful Resources  
- [Useful documentation URL]  
- [Helpful blog post]  
- [Effective tool or wordlist]

### 🏆 Perceived Difficulty  
Personal rating: [1-10]/10

Total time: [X hours]

Most challenging aspects:  
1. [Challenge 1]  
2. [Challenge 2]

---  
Additional notes:  
[Any final observation or important reminder]
"""
    with open(args.filename, "w", encoding="utf-8") as f:
        f.write(md)
    print(Fore.WHITE + f"Template saved as {args.filename}" + Style.RESET_ALL)

# ─────────────────────────────────────────────
# CLI main
def main():
    
    print(f"\n\n{bg.BLACK}{Fore.WHITE}In The Name of God {Style.RESET_ALL}\n\n")
    p = argparse.ArgumentParser(
        description="WriteupBuilder: creates a markdown write-up based on your inputs or creates a pre-written template."
    )
    p.add_argument(
        "-fn", "--filename",
        metavar="",
        default="WriteupTemplate.md",
        help="Name of the output file (default: WriteupTemplate.md)"
    )
    p.add_argument(
        "-t", "--template",
        action="store_true",
        help="Generate an advanced pre-written template for you to fill out"
    )
    args = p.parse_args()

    if args.template:
        template_builder(args)
    else:
        writeup_builder()

if __name__ == "__main__":
    main()

