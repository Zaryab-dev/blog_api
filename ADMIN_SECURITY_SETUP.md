# 🚀 Admin Security - Quick Setup

## Install & Configure (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Configure Environment
Add to `.env`:
```bash
# Get your IP
YOUR_IP=$(curl -s ifconfig.me)

# Add to .env
ADMIN_IP_RESTRICTION_ENABLED=True
ALLOWED_ADMIN_IPS=$YOUR_IP
SECURITY_EMAIL_ALERTS=True
SECURITY_ALERT_EMAIL=admin@zaryableather.com
```

### 4. Test Login
```bash
# Start server
python manage.py runserver

# Visit http://localhost:8000/admin/
# Login with credentials
# Set up 2FA with authenticator app
```

## Features Enabled

✅ **Strong Passwords** - 12+ chars, complex requirements  
✅ **2FA** - OTP via authenticator app  
✅ **Login Protection** - 5 attempts → 1 hour lockout  
✅ **IP Restriction** - Whitelist only  
✅ **Email Alerts** - Lockouts & admin logins  
✅ **Custom Login** - Branded & secure  
✅ **Session Timeout** - 15 minutes  

## Quick Commands

```bash
# Reset lockouts
python manage.py axes_reset

# Disable 2FA (emergency)
python manage.py two_factor_disable username

# Check logs
tail -f logs/security.log
```

## Troubleshooting

**Locked out?**
```bash
python manage.py axes_reset_username your_username
```

**Lost 2FA device?**
```bash
python manage.py two_factor_disable your_username
```

**Can't access admin?**
```bash
# Temporarily disable IP restriction
ADMIN_IP_RESTRICTION_ENABLED=False
```

---

See `ADMIN_SECURITY_COMPLETE.md` for full documentation.
