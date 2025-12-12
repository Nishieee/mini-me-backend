# ElevenLabs API Key Permission Fix

## Issue
Your ElevenLabs API key is missing the `text_to_speech` permission.

**Error:** `missing_permissions: The API key you used is missing the permission text_to_speech to execute this operation.`

## Solution

### Option 1: Enable Permission on Existing Key
1. Go to https://elevenlabs.io/
2. Log in to your account
3. Navigate to **Settings** → **API Keys**
4. Find your API key
5. Enable the **"text_to_speech"** permission
6. Save the changes

### Option 2: Create a New API Key with Permissions
1. Go to https://elevenlabs.io/
2. Log in to your account
3. Navigate to **Settings** → **API Keys**
4. Click **"Create New API Key"**
5. Make sure **"text_to_speech"** permission is checked
6. Copy the new API key
7. Update `keys.env` with the new key:
   ```
   ELEVEN_API_KEY=your_new_api_key_here
   ```

### Option 3: Check Your Subscription
- Some ElevenLabs plans may have limited permissions
- Ensure your subscription includes TTS API access
- Free tier may have restrictions

## After Fixing
1. Restart MiniMe: `python3 -u minime.py`
2. The error should be resolved
3. MiniMe will be able to speak responses

## Note
The code has been updated to:
- Show clearer error messages
- Continue running even if TTS fails (you'll see the text response)
- Provide helpful guidance when this error occurs

