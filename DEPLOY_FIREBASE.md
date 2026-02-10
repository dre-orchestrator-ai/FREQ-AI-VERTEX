# Deploy Dashboard to Firebase Hosting

> Goal: Get `public/index.html` live at `freq-vertex.web.app`

## Prerequisites
- Node.js installed on your Mac
- Google account with Firebase project `freq-vertex`

---

## Step-by-Step (Run These on Your Mac)

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
```

### 2. Login to Firebase
```bash
firebase login
```
This opens a browser. Sign in with your Google account that owns the `freq-vertex` project.

### 3. Navigate to Project Root
```bash
cd /path/to/FREQ-AI-VERTEX
```

### 4. Verify Firebase Config
The project already has `firebase.json` and `.firebaserc` configured. Verify:
```bash
cat .firebaserc
```
Should show:
```json
{
  "projects": {
    "default": "freq-vertex"
  }
}
```

### 5. Deploy
```bash
firebase deploy --only hosting
```

That's it. Firebase reads `firebase.json`, sees `"public": "public"`, and deploys everything in the `public/` folder.

### 6. Verify
After deploy completes, open:
- **https://freq-vertex.web.app**
- **https://freq-vertex.firebaseapp.com** (alternate URL)

Both should show the SOL Lattice Maritime Barge Drafting dashboard.

---

## If You Get Errors

### "Error: No project active"
```bash
firebase use freq-vertex
```

### "Error: Not authorized"
```bash
firebase login --reauth
```

### "Command not found: firebase"
```bash
npx firebase-tools deploy --only hosting
```

### Using Your 3D Visualization Instead
If you want to deploy the 3D barge visualization (the React+Three.js file from your Downloads) instead of the metrics dashboard:

```bash
# Back up current dashboard
cp public/index.html public/dashboard.html

# Copy your 3D viz into public/
cp "/Users/dre.orchestrator.ai/Downloads/index (6).html" public/index.html

# Deploy
firebase deploy --only hosting
```

**CDN order matters for the 3D version:**
React -> ReactDOM -> Three.js -> PropTypes@15.8.1 -> Recharts -> Babel

---

## Fallback: Netlify (If Firebase Blocked)

If Firebase CLI gives you trouble:

1. Go to https://app.netlify.com
2. Click "Add new site" > "Import an existing project"
3. Connect to GitHub > Select `dre-achitect/freq-ai-vertex`
4. Set:
   - Branch: `main` (after PR merge) or `claude/update-agent-protocol-z5o9X`
   - Publish directory: `public`
5. Click Deploy

Live URL will be: `https://[random-name].netlify.app`
You can set a custom subdomain in Site Settings.

---

*Total time: ~3 minutes if Firebase CLI is installed. ~5 minutes for Netlify.*
