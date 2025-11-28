# GitHub Pages Deployment Guide

## Quick Setup

1. **Enable GitHub Pages** in your repository settings:
   - Go to: https://github.com/adhit-r/fairmind-mcp/settings/pages
   - Source: Select **"GitHub Actions"**
   - Click **Save**

2. **Push the workflow file**:
   ```bash
   git add .github/workflows/pages.yml
   git commit -m "Add GitHub Pages deployment"
   git push
   ```

3. **Verify deployment**:
   - Go to the **Actions** tab in your repository
   - The workflow will run automatically on push to `main`/`master`
   - Once complete, your site will be available at:
     `https://adhit-r.github.io/fairmind-mcp/`

## How It Works

The workflow (`.github/workflows/pages.yml`):
1. Triggers on push to `main`/`master` branch
2. Copies `website/website.html` to `_site/index.html`
3. Deploys to GitHub Pages using the official Pages actions

## Manual Deployment

You can also trigger deployment manually:
1. Go to **Actions** tab
2. Select **"Deploy to GitHub Pages"** workflow
3. Click **"Run workflow"**

## Custom Domain (Optional)

To use a custom domain:
1. Add a `CNAME` file to the `website/` folder with your domain
2. Update the workflow to copy `CNAME` to `_site/`
3. Configure DNS in GitHub Pages settings

## Troubleshooting

- **Workflow not running?** Check that GitHub Pages is set to "GitHub Actions" source
- **404 error?** Ensure `website/website.html` exists and is committed
- **Build failing?** Check the Actions tab for error details

