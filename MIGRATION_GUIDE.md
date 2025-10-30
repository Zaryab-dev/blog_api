# 📦 Migration Guide: Local Storage → Supabase

## Overview

This guide helps you migrate existing images from local `/media/` storage to Supabase Storage.

---

## ⚠️ Current Status

Your system is already configured for Supabase-only storage:
- ✅ `ImageAsset.file` is `URLField` (stores URLs)
- ✅ Migration `0004` applied (ImageField → URLField)
- ✅ New uploads go to Supabase automatically

---

## 🔍 Check for Local Files

### 1. Check if /media/ folder has files
```bash
ls -la /Users/zaryab/django_projects/leather_api/media/
```

### 2. Check database for local paths
```python
python3 manage.py shell

from blog.models import ImageAsset

# Check for local file paths
local_images = ImageAsset.objects.filter(file__startswith='/media/')
print(f"Local images: {local_images.count()}")

# Check for Supabase URLs
supabase_images = ImageAsset.objects.filter(file__startswith='https://')
print(f"Supabase images: {supabase_images.count()}")
```

---

## 🚀 Migration Script

### Option 1: Automated Migration (Recommended)

Create `migrate_to_supabase.py`:

```python
#!/usr/bin/env python
"""
Migrate local images to Supabase Storage
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from blog.models import ImageAsset
from core.storage import supabase_storage
from django.core.files import File
from pathlib import Path

def migrate_images():
    """Migrate all local images to Supabase"""
    
    # Find images with local paths
    local_images = ImageAsset.objects.filter(
        file__startswith='/media/'
    ) | ImageAsset.objects.filter(
        file__startswith='media/'
    )
    
    total = local_images.count()
    print(f"Found {total} local images to migrate")
    
    if total == 0:
        print("✅ No local images found. All images are already in Supabase!")
        return
    
    success = 0
    failed = 0
    
    for i, image in enumerate(local_images, 1):
        print(f"\n[{i}/{total}] Migrating: {image.alt_text}")
        
        try:
            # Get local file path
            local_path = image.file.replace('/media/', 'media/')
            full_path = Path(settings.BASE_DIR) / local_path
            
            if not full_path.exists():
                print(f"  ❌ File not found: {full_path}")
                failed += 1
                continue
            
            # Open file
            with open(full_path, 'rb') as f:
                django_file = File(f)
                
                # Upload to Supabase
                url = supabase_storage.upload_file(
                    django_file,
                    folder='blog-images/',
                    filename=image.alt_text or f'image-{image.id}'
                )
            
            # Update database
            image.file = url
            image.save()
            
            print(f"  ✅ Uploaded: {url}")
            success += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Migration Complete!")
    print(f"{'='*60}")
    print(f"✅ Success: {success}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {total}")

if __name__ == '__main__':
    from django.conf import settings
    migrate_images()
```

Run migration:
```bash
python3 migrate_to_supabase.py
```

---

### Option 2: Manual Migration

For each image:

```python
from blog.models import ImageAsset
from core.storage import supabase_storage
from django.core.files import File

# Get image
image = ImageAsset.objects.get(id='your-image-id')

# Open local file
with open(f'media/{image.file}', 'rb') as f:
    django_file = File(f)
    
    # Upload to Supabase
    url = supabase_storage.upload_file(
        django_file,
        folder='blog-images/',
        filename=image.alt_text
    )

# Update database
image.file = url
image.save()

print(f"Migrated: {url}")
```

---

## 🧹 Cleanup After Migration

### 1. Verify all images migrated
```python
from blog.models import ImageAsset

# Should be 0
local_count = ImageAsset.objects.filter(
    file__startswith='/media/'
).count()

# Should be > 0
supabase_count = ImageAsset.objects.filter(
    file__startswith='https://'
).count()

print(f"Local: {local_count}")
print(f"Supabase: {supabase_count}")
```

### 2. Backup local files (optional)
```bash
# Create backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Move to safe location
mv media_backup_*.tar.gz ~/backups/
```

### 3. Delete local files
```bash
# ⚠️ Only after verifying migration!
rm -rf media/images/
rm -rf media/blog/
```

### 4. Update .gitignore
```bash
# Add to .gitignore
echo "media/" >> .gitignore
```

---

## ✅ Verification Checklist

After migration:

- [ ] All ImageAsset records have Supabase URLs
- [ ] No records with `/media/` paths
- [ ] Images display correctly in admin
- [ ] Featured images display in posts
- [ ] Test upload creates Supabase URL
- [ ] Local `/media/` folder backed up
- [ ] Local files deleted (optional)

---

## 🔄 Rollback Plan

If migration fails:

### 1. Restore from backup
```bash
tar -xzf media_backup_YYYYMMDD.tar.gz
```

### 2. Revert database changes
```python
# If you kept track of changes
from blog.models import ImageAsset

# Restore old URLs from backup
# (You should have a backup of the database too)
```

### 3. Check Django migrations
```bash
python3 manage.py showmigrations blog
```

---

## 📊 Migration Statistics

Track your migration:

```python
from blog.models import ImageAsset
from django.db.models import Q

# Total images
total = ImageAsset.objects.count()

# Supabase images
supabase = ImageAsset.objects.filter(
    file__startswith='https://'
).count()

# Local images
local = ImageAsset.objects.filter(
    Q(file__startswith='/media/') | 
    Q(file__startswith='media/')
).count()

# Calculate percentage
percentage = (supabase / total * 100) if total > 0 else 0

print(f"Total Images: {total}")
print(f"Supabase: {supabase} ({percentage:.1f}%)")
print(f"Local: {local}")
```

---

## 🐛 Troubleshooting

### Migration Script Fails

**Error: File not found**
```python
# Check file path
import os
from pathlib import Path
from django.conf import settings

file_path = Path(settings.BASE_DIR) / 'media' / 'your-file.jpg'
print(f"Exists: {file_path.exists()}")
print(f"Path: {file_path}")
```

**Error: Upload failed**
```python
# Check Supabase credentials
from django.conf import settings
print(f"URL: {settings.SUPABASE_URL}")
print(f"Bucket: {settings.SUPABASE_BUCKET}")

# Test upload
from core.storage import supabase_storage
# Try manual upload
```

### Images Not Displaying After Migration

1. Check URL format:
   ```python
   image = ImageAsset.objects.first()
   print(image.file)
   # Should be: https://soccrpfkqjqjaoaturjb.supabase.co/storage/...
   ```

2. Verify bucket is public in Supabase Dashboard

3. Test URL in browser

---

## 📝 Best Practices

### Before Migration
1. ✅ Backup database
2. ✅ Backup `/media/` folder
3. ✅ Test migration on staging first
4. ✅ Verify Supabase credentials
5. ✅ Check Supabase storage quota

### During Migration
1. ✅ Run in batches (not all at once)
2. ✅ Log all operations
3. ✅ Handle errors gracefully
4. ✅ Verify each upload

### After Migration
1. ✅ Verify all images migrated
2. ✅ Test image display
3. ✅ Keep backup for 30 days
4. ✅ Monitor Supabase usage
5. ✅ Update documentation

---

## 🎯 Summary

### If You Have Local Images
1. Run migration script
2. Verify all images migrated
3. Backup local files
4. Delete local files (optional)

### If You Don't Have Local Images
✅ **You're all set!** Your system is already configured for Supabase-only storage.

---

## 📞 Support

If migration fails:
1. Check logs: `tail -f logs/django.log`
2. Verify Supabase credentials
3. Test manual upload
4. Review error messages
5. Restore from backup if needed

---

## ✅ Current Status

Your system is **ready for Supabase-only storage**:
- ✅ Database schema updated (URLField)
- ✅ Upload endpoints configured
- ✅ Admin panel integrated
- ✅ Storage utility ready
- ✅ All tests passing

**New uploads automatically go to Supabase!** 🎉
