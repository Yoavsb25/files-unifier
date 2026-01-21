# GitHub Actions Workflows

## Deploy to GitHub Pages

The `deploy.yml` workflow automatically runs tests and deploys the PDF Merger UI to GitHub Pages whenever code is pushed to the `main` branch.

### How It Works

1. **Trigger**: Runs automatically on push to `main` branch
2. **Manual Trigger**: Can also be triggered manually from the Actions tab
3. **Test Phase**: Runs all unit tests using pytest
4. **Deployment**: Only proceeds if all tests pass, then uploads static files and deploys to GitHub Pages
5. **Files Deployed**:
   - `index.html`
   - `styles.css`
   - `app.js`
   - `.nojekyll`

### Workflow Steps

1. **Test Job**:
   - Checks out the repository
   - Sets up Python 3.9
   - Installs dependencies from `requirements.txt`
   - Runs all unit tests with pytest
   - Fails the workflow if any tests fail

2. **Deploy Job** (only runs if tests pass):
   - Checks out the repository
   - Sets up GitHub Pages
   - Uploads UI files as artifact
   - Deploys to GitHub Pages

### Setup

1. Ensure GitHub Pages is enabled in repository settings:
   - Go to **Settings** → **Pages**
   - Under **Source**, select **GitHub Actions**

2. Push to main branch - deployment happens automatically!

### Monitoring

- Check the **Actions** tab to see workflow runs
- View deployment status and logs
- See the deployment URL in the workflow summary

### Troubleshooting

**If tests fail:**
- Check the Actions tab for test output and error messages
- Run tests locally: `pytest tests/ -v`
- Ensure all dependencies are in `requirements.txt`
- Fix failing tests before deployment will proceed

**If deployment fails:**
- Check the Actions tab for error messages
- Ensure GitHub Pages is set to use "GitHub Actions" as source
- Verify all required files exist in the repository root
- Check repository permissions (Pages write access required)
- Note: Deployment will not run if tests fail
