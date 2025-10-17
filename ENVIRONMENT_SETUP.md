# Environment Setup Guide

## Required Environment Variables

These variables **MUST** be set before running the application. The application will fail to start if any required variables are missing.

### Critical Settings (Required)

#### 1. **SUPABASE_URL**
- **Description**: Your Supabase project URL
- **Example**: `https://yourproject.supabase.co`
- **How to get**: Supabase Dashboard → Settings → API → Project URL

#### 2. **SUPABASE_API_KEY**
- **Description**: Your Supabase anon/public API key
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **How to get**: Supabase Dashboard → Settings → API → anon/public key
- **Security**: Never commit this to version control

#### 3. **SUPABASE_BUCKET**
- **Description**: Storage bucket name for file uploads
- **Example**: `blog_storage`
- **How to get**: Create a bucket in Supabase Dashboard → Storage

#### 4. **SECRET_KEY**
- **Description**: Django secret key for cryptographic signing
- **Example**: Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- **Security**: Must be unique and kept secret

#### 5. **DEBUG**
- **Description**: Enable/disable debug mode
- **Values**: `True` (development only) or `False` (production)
- **Default**: `False` (safe default)
- **Warning**: NEVER set to `True` in production

### Setup Instructions

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in all required values:**
   - Open `.env` in your editor
   - Replace all placeholder values with actual credentials
   - Save the file

3. **Verify configuration:**
   ```bash
   python manage.py check
   ```
   
   If any required variables are missing, you'll see a clear error message.

4. **Never commit `.env` to version control:**
   - The `.env` file is already in `.gitignore`
   - Only commit `.env.example` as a template

### Development vs Production

#### Development (.env.development)
```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

#### Production (.env.production)
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
SECURE_PROXY_SSL_HEADER_ENABLED=True
```

### Security Best Practices

1. **Never hardcode secrets** in source code
2. **Use strong, unique values** for SECRET_KEY
3. **Rotate credentials regularly** (every 90 days)
4. **Use different credentials** for dev/staging/production
5. **Enable 2FA** on all service accounts (Supabase, AWS, etc.)
6. **Monitor access logs** for suspicious activity

### Troubleshooting

#### Error: "Missing required environment variables"
- Check that all required variables are set in `.env`
- Verify `.env` is in the project root directory
- Ensure no typos in variable names

#### Error: "Invalid Supabase credentials"
- Verify URL and API key are correct
- Check that the bucket exists and is accessible
- Ensure API key has proper permissions

#### Error: "DEBUG mode enabled in production"
- Set `DEBUG=False` in production environment
- Never override DEBUG in settings.py

### Support

For issues or questions:
1. Check this documentation
2. Review Django security best practices
3. Verify all credentials are correct
4. Check application logs for detailed errors
