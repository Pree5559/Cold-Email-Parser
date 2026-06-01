# Streamlit Cloud Deployment Guide

This guide walks you through deploying **The Closer** to [Streamlit Community Cloud](https://streamlit.io/cloud).

## Prerequisites

1. GitHub repository pushed (✅ Already done at `https://github.com/Pree5559/Cold-Email-Parser.git`)
2. Streamlit Community Cloud account (free signup at https://share.streamlit.io/)
3. Environment variables configured

## Step 1: Set Up Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account (or create one)
3. Click **"New app"**
4. Select:
   - **Repository:** `Pree5559/Cold-Email-Parser`
   - **Branch:** `main`
   - **Main file path:** `phase4/streamlit_app.py`

> ⚠️ Add `runtime.txt` to the repo root before deploying to force a compatible Python version. Use `python-3.11.16` for Streamlit Cloud.

5. Click **"Deploy"** — Streamlit will build and deploy your app

## Step 2: Configure Environment Variables (Secrets)

⚠️ **Important:** Never commit sensitive data (`.env` file) to GitHub. Use Streamlit Secrets instead.

1. In the Streamlit app dashboard, click the **⋮ (three dots)** menu → **Settings**
2. Go to **Secrets** tab
3. Add your environment variables in the TOML format:

```toml
# SMTP Configuration (required)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your-gmail@gmail.com"
SMTP_PASSWORD = "your-16-char-app-password"
SENDER_NAME = "Your Name"

# Email Sending (optional)
DRY_RUN = "True"  # Set to "False" to actually send emails

# LLM Enhancement (optional)
# GROQ_API_KEY = "your-groq-api-key"
```

> **Gmail App Password Setup:**
> 1. Enable 2-Factor Authentication on your Google Account
> 2. Go to Google Account > Security > 2-Step Verification
> 3. Select "App passwords"
> 4. Create new app password (name it "The Closer")
> 5. Copy the 16-character app password to `SMTP_PASSWORD` above

4. Click **Save**
5. Your app will automatically restart with the new secrets

## Step 3: Test Locally (Optional)

Before deploying, test locally with Streamlit secrets:

1. Create `.streamlit/secrets.toml` in your project:
   ```bash
   mkdir -p .streamlit
   echo "SMTP_USER = 'your-email@gmail.com'" > .streamlit/secrets.toml
   # ... add other secrets
   ```

2. Run locally:
   ```bash
   streamlit run phase4/streamlit_app.py
   ```

3. Access at `http://localhost:8501`

> **Note:** `.streamlit/secrets.toml` is in `.gitignore` (not pushed to GitHub).

## Step 4: Access Your Deployed App

Your app is live at:
```
https://cold-email-parser-<your-username>.streamlit.app
```

Share this URL with collaborators.

## Step 5: Monitor and Troubleshoot

- **View Logs:** In the app dashboard, click **Manage app** → **View logs**
- **Restart App:** Click **Rerun** or modify a file and push to GitHub (auto-deploys)
- **Check Secrets:** Verify environment variables are correctly set in the Secrets tab

## Troubleshooting

### "Configuration error: SMTP_USER is required"

**Problem:** Secrets not loaded into the app.

**Solution:** 
1. Verify secrets are in the correct TOML format (no quotes around keys)
2. Click **Save** in the Secrets tab
3. Wait 5-10 seconds, then refresh the app

### "Email validation failed"

**Problem:** Contact data is malformed.

**Solution:**
1. Upload a JSON or CSV file with correct format:
   ```json
   [
     {
       "recipient_email": "john@example.com",
       "company": "TechCorp",
       "role": "Software Engineer",
       "recipient_name": "John Doe",
       "candidate_name": "Your Name",
       "candidate_background": "Full-stack developer with 5 years experience",
       "portfolio_url": "https://github.com/yourname"
     }
   ]
   ```

### "Failed to send email: SMTP error"

**Problem:** SMTP credentials are invalid.

**Solution:**
1. Verify `SMTP_USER` and `SMTP_PASSWORD` are correct
2. For Gmail, ensure:
   - 2-Factor Authentication is enabled
   - You used an App Password (not your regular Gmail password)
3. Re-save secrets and restart the app

### App is very slow or times out

**Problem:** Large contact lists or slow email sending.

**Solution:**
1. Use smaller batches (split CSV into smaller files)
2. Set `DRY_RUN = "True"` for testing (skips actual SMTP)
3. Streamlit Cloud has a 12GB memory limit and 24-hour session limit

## Appendix: Local Development & Iteration

To iterate locally and sync changes:

```bash
# Make changes locally
git add .
git commit -m "Update email templates"
git push origin main

# Streamlit Cloud auto-deploys within 30 seconds
```

## Support

- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Community Forum:** https://discuss.streamlit.io/
- **GitHub Issues:** Open an issue on the repo

---

Happy cold emailing! 📧
