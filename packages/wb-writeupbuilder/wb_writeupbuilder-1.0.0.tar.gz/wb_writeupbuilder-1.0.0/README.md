# LAS - LoginAuthSessionizer

**LAS (LoginAuthSessionizer)** is a command-line tool that intelligently detects login forms, submits credentials, and saves session cookies and headers for later use in a .json file.

💡 Supports non-standard login layouts, custom headers, cookies, and verbose HTML inspection.

#### - This tool was mainly made for Using with [FF-FlagFinder](https://github.com/Ph4nt01/FF-FlagFinder) -


---

## 🚀 Workflow
- Detects login form fields
- Authenticate with user credentials
- Save the Session in session.json for using it with [FF-FlagFinder](https://github.com/Ph4nt01/FF-FlagFinder) or tools like `requests`, `httpx`, `curl`.

---

## 📦 Installation

### Using `pipx` (recommended)

```bash
pipx install las-loginauthsessionizer
````

### Using `pip`

```bash
pip install las-loginauthsessionizer
```

---

## ⚙️ Usage

```bash
las -u https://target.com/login
```

### With verbose output:

```bash
las -u https://target.com/login -v
```

### With custom headers and cookies:

```bash
las \
  -u https://target.com/login \
  -un root -pw toor \
  -hd "User-Agent: Custom" \
  -ck sessionid=123456
```

---

## 🧪 Output Example

```
LAS-LoginAuthSessionizer

[*] [verbose] Dumping form‐like containers:

[*] Container #2: <form action='doLogin' method='POST'>
<input type='text' name='uid' value=''>
<input type='password' name='passw' value=''>
<input type='submit' name='btnSubmit' value='Login'>

[+] Detected login form action URL: [https://target.com/doLogin]

[+] Detected login fields: {'uid': 'admin', 'passw': 'admin'}

[+] Detected login form structure: <form>

Login status: 200 OK
[+] Login Successful

Session saved to: [session.json]
```

---

## 📥 Output: Session File

A JSON file (default: `session.json`) will be saved, containing:

```json
{
  "cookies": {
    "sessionid": "abc123"
  },
  "headers": {
    "User-Agent": "Mozilla/5.0 ..."
  }
}
```

---

## 🔧 CLI Options

| Option                 | Description                                       |
| ---------------------- | ------------------------------------------------- |
| `-u`, `--url`          | Target login page URL (required)                  |
| `-un`, `--username`    | Username to use in login (default: `admin`)       |
| `-pw`, `--password`    | Password to use in login (default: `admin`)       |
| `-v`, `--verbose`      | Enable verbose output                             |
| `-ck`, `--cookie`      | Add cookies in `key=value` format                 |
| `-hd`, `--header`      | Add headers in `Key: Value` format                |
| `-s`, `--session-file` | Output file for session (default: `session.json`) |

---

## 📂 Project Structure

```
LAS-LoginAuthSessionizer/
├── las/
│   ├── __init__.py
│   └── cli.py
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
```

---

## 📜 Author

[Ph4nt01](https://github.com/Ph4nt01)
