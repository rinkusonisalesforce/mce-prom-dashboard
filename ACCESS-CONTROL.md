# 🔐 Access Control - Adding Team Members

## Recommended Approach: Private + Collaborators

Make the repo **Private** and add specific users who need access.

---

## ✅ Step 1: Create Private Repository

When creating on GitHub:
```
Visibility: ● Private
```

---

## 👥 Step 2: Add Collaborators

### Via GitHub Website

1. Go to your repo: `https://github.com/YOUR_USERNAME/mce-prom-dashboard`

2. Click **Settings** (top menu)

3. Click **Collaborators** (left sidebar)

4. Click **Add people**

5. Enter GitHub username or email:
   ```
   john.doe@salesforce.com
   jane.smith@salesforce.com
   ```

6. Choose permission level:
   - **Read** - View only, can clone
   - **Write** - Can push changes (recommended for team)
   - **Admin** - Full control

7. Click **Add [username] to this repository**

### Via GitHub CLI

```bash
# Add with Write access
gh repo add-collaborator YOUR_USERNAME/mce-prom-dashboard username1 --permission push

# Add with Read access
gh repo add-collaborator YOUR_USERNAME/mce-prom-dashboard username2 --permission pull
```

---

## 🏢 Step 3: Use GitHub Organization (Best for Teams)

For larger teams, create an **Organization**:

### Create Organization

1. Go to: https://github.com/organizations/plan
2. Choose **Free** plan
3. Name: `salesforce-mce-team` (or similar)
4. Add members

### Transfer Repository to Org

1. Repo → **Settings** → **General**
2. Scroll to **Danger Zone**
3. Click **Transfer**
4. Enter org name
5. Confirm

Now the repo is at: `https://github.com/salesforce-mce-team/mce-prom-dashboard`

### Benefits

✅ Team-owned (not tied to your personal account)  
✅ Centralized access management  
✅ Multiple repos under one organization  
✅ Better for long-term maintenance  

---

## 🆚 Public vs Private

### Private Repository ✅ (Recommended)

**Pros:**
- ✅ Control exactly who has access
- ✅ Add/remove collaborators anytime
- ✅ Safe for internal Salesforce tools
- ✅ Free for unlimited collaborators

**Cons:**
- ⚠️ Team needs GitHub accounts
- ⚠️ Need to add each person manually

**When to use:**
- Internal Salesforce tools
- Contains Org62/UTDP references
- Want controlled access

### Public Repository

**Pros:**
- ✅ Anyone can view/clone
- ✅ No access management needed
- ✅ Good for open source

**Cons:**
- ❌ Exposes Salesforce internal tool names
- ❌ Anyone can see your code
- ❌ Can't control who forks it

**When to use:**
- Open source projects
- Public documentation
- Community tools

---

## 🔒 What's Safe in a Private Repo?

### ✅ Safe to Include

- Source code (React components)
- Configuration (Org62 URL - it's internal anyway)
- SOQL queries
- Documentation
- Build scripts
- Static aggregated data (mceRealData.js)

### ❌ Never Include (Even in Private)

- Session cookies / tokens
- Raw CSV files with customer data
- API credentials
- Passwords
- Personal access tokens

**Good news:** Your `.gitignore` already blocks these!

---

## 📋 Access Levels Explained

### Read Access
```
Can:
- View code
- Clone repo
- Download releases
- Create issues

Cannot:
- Push changes
- Merge PRs
- Change settings
```

**Use for:** Viewers, stakeholders, read-only users

### Write Access
```
Can:
- Everything in Read
- Push commits
- Create branches
- Open/close issues
- Merge PRs

Cannot:
- Delete repo
- Change settings
- Add collaborators
```

**Use for:** Active developers, team members

### Admin Access
```
Can:
- Everything in Write
- Delete repo
- Change settings
- Add collaborators
- Transfer ownership
```

**Use for:** Repository owners, team leads

---

## 👥 Common Access Patterns

### Small Team (2-5 people)
```
Private repo
Owner: You (Admin)
Team: Write access
Stakeholders: Read access
```

### Medium Team (6-20 people)
```
Organization-owned repo
Admins: 2-3 team leads
Developers: Write access (via team)
Viewers: Read access (via team)
```

### Large Team (20+ people)
```
Organization with Teams
- @mce-developers (Write)
- @mce-leads (Admin)
- @mce-viewers (Read)
```

---

## 🔄 Managing Access Over Time

### Add New Team Member

```bash
# Via CLI
gh repo add-collaborator YOUR_USERNAME/mce-prom-dashboard new-user --permission push

# Via Web
Repo → Settings → Collaborators → Add people
```

### Remove Access

```bash
# Via CLI
gh repo remove-collaborator YOUR_USERNAME/mce-prom-dashboard old-user

# Via Web
Repo → Settings → Collaborators → Click X next to user
```

### Change Permission Level

```bash
# Via Web (easiest)
Repo → Settings → Collaborators → Dropdown next to user → Select new level
```

---

## 📊 Sharing Options Summary

| Method | Access | Best For |
|--------|--------|----------|
| **Private + Collaborators** | Controlled | Small teams (2-10) |
| **Organization** | Team-based | Medium/large teams |
| **Public** | Everyone | Open source only |
| **Internal (Enterprise)** | Company-only | Enterprise GitHub |

---

## 🎯 Recommended Setup for MCE Dashboard

### For Your Use Case:

```
✅ Create: Private repository
✅ Owner: Your personal account (or create org)
✅ Add: Specific team members as collaborators
✅ Permission: Write (so they can contribute)
✅ Optional: Add stakeholders with Read access
```

### Why This Works:

1. **Private** - Keeps Salesforce internal tool references contained
2. **Collaborators** - Easy to manage 5-10 team members
3. **Write access** - Team can contribute and update data
4. **Can change later** - Easy to transfer to org if team grows

---

## 🚀 Quick Start

```bash
# 1. Create private repo on GitHub
# Visibility: Private

# 2. Push code
git remote add origin https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
git push -u origin main

# 3. Add team members
# Repo → Settings → Collaborators → Add people

# 4. Share URL with team
# They can clone:
git clone https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
```

---

## ✅ Access Control Checklist

Before sharing:

- [ ] Repository is Private
- [ ] Added all team members as collaborators
- [ ] Set correct permission levels (Write for developers)
- [ ] .gitignore blocks sensitive files
- [ ] No credentials in code
- [ ] README explains how to use it
- [ ] Team knows how to build extension

---

**Ready to create your private repo and add collaborators!** 🔐
