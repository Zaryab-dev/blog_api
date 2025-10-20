#!/usr/bin/env python3
"""
Pre-Deployment Verification Script
Checks if all critical files and configurations are ready for AWS App Runner deployment
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"{GREEN}✓{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {filepath} NOT FOUND")
        return False

def check_file_content(filepath, search_strings, description):
    """Check if file contains specific strings"""
    if not os.path.exists(filepath):
        print(f"{RED}✗{RESET} {description}: File not found")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    missing = []
    for search_str in search_strings:
        if search_str not in content:
            missing.append(search_str)
    
    if missing:
        print(f"{RED}✗{RESET} {description}: Missing {', '.join(missing)}")
        return False
    else:
        print(f"{GREEN}✓{RESET} {description}")
        return True

def main():
    print_header("AWS App Runner Deployment Verification")
    
    base_dir = Path(__file__).parent
    all_checks_passed = True
    
    # Check 1: Critical Files
    print(f"\n{YELLOW}[1] Checking Critical Files{RESET}")
    files_to_check = [
        ('Dockerfile', 'Dockerfile'),
        ('docker-entrypoint.sh', 'Docker entrypoint script'),
        ('gunicorn.conf.py', 'Gunicorn configuration'),
        ('requirements.txt', 'Python dependencies'),
        ('manage.py', 'Django management script'),
        ('leather_api/settings.py', 'Django settings'),
        ('leather_api/urls.py', 'Main URL configuration'),
        ('blog/views_simple_health.py', 'Simple health check view'),
    ]
    
    for filepath, description in files_to_check:
        if not check_file(base_dir / filepath, description):
            all_checks_passed = False
    
    # Check 2: Health Check Configuration
    print(f"\n{YELLOW}[2] Checking Health Check Configuration{RESET}")
    
    # Check if simple_healthcheck is imported correctly
    urls_file = base_dir / 'leather_api' / 'urls.py'
    if check_file_content(
        urls_file,
        ['from blog.views_simple_health import simple_healthcheck', 
         "path('api/v1/healthcheck/', simple_healthcheck"],
        'Health check import and routing'
    ):
        print(f"{GREEN}  → Health check correctly configured at /api/v1/healthcheck/{RESET}")
    else:
        all_checks_passed = False
        print(f"{RED}  → CRITICAL: Health check not properly configured!{RESET}")
    
    # Check simple health check doesn't have DB queries
    health_file = base_dir / 'blog' / 'views_simple_health.py'
    with open(health_file, 'r') as f:
        health_content = f.read()
    
    if 'connection.cursor()' in health_content or 'SELECT 1' in health_content:
        print(f"{RED}✗ Simple health check contains database queries!{RESET}")
        all_checks_passed = False
    else:
        print(f"{GREEN}✓ Simple health check is database-free (fast){RESET}")
    
    # Check 3: Dockerfile Configuration
    print(f"\n{YELLOW}[3] Checking Dockerfile{RESET}")
    dockerfile = base_dir / 'Dockerfile'
    dockerfile_checks = [
        ('EXPOSE 8080', 'Port 8080 exposed'),
        ('HEALTHCHECK', 'Health check configured'),
        ('/api/v1/healthcheck/', 'Health check path correct'),
    ]
    
    for search_str, description in dockerfile_checks:
        if not check_file_content(dockerfile, [search_str], description):
            all_checks_passed = False
    
    # Check 4: Docker Entrypoint
    print(f"\n{YELLOW}[4] Checking Docker Entrypoint{RESET}")
    entrypoint = base_dir / 'docker-entrypoint.sh'
    
    if check_file_content(
        entrypoint,
        ['exec gunicorn', '--bind 0.0.0.0:$PORT', 'leather_api.wsgi:application'],
        'Gunicorn starts correctly'
    ):
        print(f"{GREEN}  → Gunicorn will start immediately{RESET}")
    else:
        all_checks_passed = False
    
    # Check if entrypoint is executable
    if os.access(entrypoint, os.X_OK):
        print(f"{GREEN}✓ docker-entrypoint.sh is executable{RESET}")
    else:
        print(f"{YELLOW}⚠ docker-entrypoint.sh is not executable (will be fixed in Docker){RESET}")
    
    # Check 5: Settings Configuration
    print(f"\n{YELLOW}[5] Checking Django Settings{RESET}")
    settings = base_dir / 'leather_api' / 'settings.py'
    settings_checks = [
        ('ALLOWED_HOSTS', 'ALLOWED_HOSTS configured'),
        ('DATABASES', 'Database configuration present'),
        ('SUPABASE_URL', 'Supabase configuration present'),
        ('gunicorn', 'Gunicorn in requirements'),
    ]
    
    for search_str, description in settings_checks:
        if search_str == 'gunicorn':
            if not check_file_content(base_dir / 'requirements.txt', [search_str], description):
                all_checks_passed = False
        else:
            if not check_file_content(settings, [search_str], description):
                all_checks_passed = False
    
    # Check 6: Environment Variables Template
    print(f"\n{YELLOW}[6] Checking Environment Configuration{RESET}")
    if check_file(base_dir / '.env.apprunner', 'App Runner environment template'):
        print(f"{GREEN}  → Use this file for App Runner environment variables{RESET}")
    else:
        print(f"{YELLOW}⚠ .env.apprunner not found (optional){RESET}")
    
    # Check 7: Deployment Script
    print(f"\n{YELLOW}[7] Checking Deployment Script{RESET}")
    deploy_script = base_dir / 'DEPLOY_TO_APPRUNNER.sh'
    if check_file(deploy_script, 'Deployment script'):
        if os.access(deploy_script, os.X_OK):
            print(f"{GREEN}✓ Deployment script is executable{RESET}")
        else:
            print(f"{YELLOW}⚠ Deployment script not executable. Run: chmod +x DEPLOY_TO_APPRUNNER.sh{RESET}")
    else:
        all_checks_passed = False
    
    # Final Summary
    print_header("Verification Summary")
    
    if all_checks_passed:
        print(f"{GREEN}✓ ALL CHECKS PASSED!{RESET}")
        print(f"\n{GREEN}Your application is ready for AWS App Runner deployment.{RESET}")
        print(f"\n{BLUE}Next steps:{RESET}")
        print(f"1. Edit DEPLOY_TO_APPRUNNER.sh with your AWS Account ID")
        print(f"2. Run: ./DEPLOY_TO_APPRUNNER.sh")
        print(f"3. Create App Runner service in AWS Console")
        print(f"4. Add environment variables from .env.apprunner")
        print(f"\n{BLUE}See COMPLETE_DEPLOYMENT_GUIDE.md for detailed instructions.{RESET}")
        return 0
    else:
        print(f"{RED}✗ SOME CHECKS FAILED{RESET}")
        print(f"\n{RED}Please fix the issues above before deploying.{RESET}")
        print(f"\n{YELLOW}Need help? Check COMPLETE_DEPLOYMENT_GUIDE.md{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
