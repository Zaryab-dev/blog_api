# Supabase Bucket Setup Guide

## Current Status

✅ Supabase client connected successfully  
✅ Public URL generation working  
⚠️ Upload requires bucket policy configuration

## Quick Fix

The upload is failing due to Row-Level Security (RLS) policy. You need to configure the bucket permissions in Supabase.

### Option 1: Use Service Role Key (Recommended for Admin)

Update your `.env` file:

```env
# Replace the anon key with service_role key
SUPABASE_API_KEY=your-service-role-key-here
```

**Where to find it:**
1. Go to Supabase Dashboard
2. Project Settings → API
3. Copy `service_role` key (not `anon` key)
4. Paste in `.env`

### Option 2: Configure Bucket Policies

If you want to keep using the anon key, add these policies in Supabase:

1. Go to Supabase Dashboard → Storage → Policies
2. Click on `leather_api_storage` bucket
3. Add these policies:

**Policy 1: Allow Authenticated Uploads**
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'leather_api_storage');
```

**Policy 2: Allow Public Read**
```sql
CREATE POLICY "Allow public read"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'leather_api_storage');
```

**Policy 3: Allow Authenticated Delete**
```sql
CREATE POLICY "Allow authenticated delete"
ON storage.objects
FOR DELETE
TO authenticated
USING (bucket_id = 'leather_api_storage');
```

### Option 3: Disable RLS (Not Recommended for Production)

1. Go to Storage → `leather_api_storage`
2. Click "Policies"
3. Disable RLS (only for testing)

## Verify Setup

After applying one of the options above, run:

```bash
python3 test_supabase_upload.py
```

Expected output:
```
✓ PASS - Connection
✓ PASS - Public URL
✓ PASS - Upload

All tests passed!
```

## Current Configuration

Your current settings from `.env`:
- **URL:** https://soccrpfkqjqjaoaturjb.supabase.co
- **Bucket:** leather_api_storage
- **Key Type:** anon (needs service_role for admin uploads)

## Recommended Setup for Production

```env
# Use service_role key for Django admin uploads
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=<your-service-role-key>
SUPABASE_BUCKET=leather_api_storage
```

This allows Django admin users to upload without complex RLS policies.

## Next Steps

1. ✅ Get service_role key from Supabase Dashboard
2. ✅ Update `.env` with service_role key
3. ✅ Run test: `python3 test_supabase_upload.py`
4. ✅ Test in Django admin: `/admin/blog/post/add/`
5. ✅ Upload image via CKEditor
6. ✅ Verify in Supabase Storage dashboard

## Support

If issues persist:
- Check Supabase logs in Dashboard → Logs
- Verify bucket exists and is named correctly
- Ensure API key is valid and not expired
