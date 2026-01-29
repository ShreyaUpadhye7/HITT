# 📤 Git Commands to Push Your Changes

## **Files I've Updated:**
- ✅ `server/server.js` - Fixed CORS configuration
- ✅ `client/.env` - Added correct API URL
- ✅ `server/.env` - Updated environment variables
- ✅ `analysis_service/render.yaml` - Deployment config

---

## **🔥 QUICK PUSH COMMANDS:**

Open your terminal in the project root and run these commands:

```bash
# Add all changes
git add .

# Commit with a descriptive message
git commit -m "Fix deployment issues: update CORS, API URLs, and environment config"

# Push to GitHub
git push origin main
```

**Alternative if your branch is different:**
```bash
git push origin master
```

---

## **🔍 Check What Changed:**

Before pushing, you can see what I changed:
```bash
# See what files were modified
git status

# See the actual changes
git diff
```

---

## **⚡ After Pushing:**

1. **Vercel**: Will automatically redeploy your frontend
2. **Render**: Will automatically redeploy your backend
3. **Wait 2-3 minutes** for deployments to complete
4. **Test your app**: Registration should work now!

---

## **🆘 If Git Commands Don't Work:**

### **Problem: "Nothing to commit"**
```bash
git add -A
git commit -m "Fix deployment configuration"
git push
```

### **Problem: "Not a git repository"**
```bash
git init
git remote add origin YOUR_GITHUB_REPO_URL
git add .
git commit -m "Fix deployment issues"
git push -u origin main
```

### **Problem: "Permission denied"**
Make sure you're logged into GitHub:
```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@gmail.com"
```

---

## **✅ VERIFICATION:**

After pushing, check:
1. **GitHub**: See if files updated
2. **Vercel**: Check deployment status
3. **Render**: Check if backend redeployed
4. **Test**: Try registration on your frontend

**Your app should work perfectly after this push! 🎉**