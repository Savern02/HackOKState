Create users script

This folder contains a small script to generate test users and create them via the running Flask app's `/signup` endpoint.

Requirements
- Python 3.8+
- `requests` (install with `pip install requests`)

Quick usage

From the project root, with your Flask app running (default: http://localhost:5000):

PowerShell example:

```powershell
# create 20 users against local server
python .\scripts\create_users.py --count 20

# use a different base URL
$env:BASE_URL = 'http://127.0.0.1:5000'
python .\scripts\create_users.py --count 50
```

Options
- --count / -n : number of users to create (default 10)
- --base-url / -b : base URL of your running server (default taken from BASE_URL env or http://localhost:5000)
- --domain / -d : email domain to use for generated addresses (default example.com)
- --start : start index for username/email numbering
- --password-length : length of generated passwords
- --dry-run : show POSTs without sending them

Notes
- The script posts form-encoded data to `/signup` (fields: email, username, password) to match the app's `auth.signup` view.
- If you prefer to create users directly via the database, let me know and I can add a script that uses the project models and `create_app()` to insert users directly.
