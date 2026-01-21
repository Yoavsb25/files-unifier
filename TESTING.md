# Local Testing Guide

This guide explains how to test the PDF Merger UI locally on your computer before deploying to GitHub Pages.

## Quick Start (Python HTTP Server)

Since you already have Python installed, the easiest way is to use Python's built-in HTTP server:

### Python 3

```bash
# Navigate to your project directory
cd /Users/yoavsborovsky/Documents/GitHub/files_unifeder

# Start the server (Python 3)
python3 -m http.server 8000
```

### Python 2 (if needed)

```bash
python -m SimpleHTTPServer 8000
```

### Access the UI

1. Open your web browser
2. Navigate to: `http://localhost:8000`
3. You should see the PDF Merger UI

### Stop the Server

Press `Ctrl+C` in the terminal to stop the server.

## Alternative Methods

### Option 2: Node.js http-server

If you have Node.js installed:

```bash
# Install http-server globally (one time)
npm install -g http-server

# Run the server
http-server -p 8000
```

### Option 3: VS Code Live Server Extension

1. Install the "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### Option 4: PHP Built-in Server

If you have PHP installed:

```bash
php -S localhost:8000
```

## Testing Checklist

When testing locally, verify:

- [ ] UI loads correctly with all sections visible
- [ ] File picker works for CSV/Excel files
- [ ] Folder picker works for PDF files
- [ ] Toggles and buttons respond to clicks
- [ ] CSV file parsing works correctly
- [ ] Excel file parsing works correctly
- [ ] PDF files are found and matched correctly
- [ ] PDF merging works and files download
- [ ] Progress bar updates during processing
- [ ] Log panel shows messages correctly
- [ ] Summary panel updates with counts

## Important Notes

### Browser Compatibility

- **Chrome/Edge**: Full support, recommended for testing
- **Firefox**: Full support
- **Safari**: Full support (may need to enable file access in settings)
- **Opera**: Full support

### File Access

Modern browsers require a web server to access local files due to security restrictions. **Do not** try to open `index.html` directly with `file://` protocol - it won't work properly with file reading APIs.

### CORS and File Reading

The application uses the File API which works fine with local servers. No CORS issues should occur when using a local HTTP server.

### Testing with Sample Data

Create test files to verify functionality:

1. **Sample CSV** (`test_data.csv`):
   ```csv
   serial_numbers
   file1,file2,file3
   file2,file4
   ```

2. **Sample PDFs**: Create a few test PDF files named `file1.pdf`, `file2.pdf`, etc.

3. **Test the workflow**:
   - Select the CSV file
   - Select the folder with PDFs
   - Click "Run Merge"
   - Verify merged PDFs download correctly

## Troubleshooting

### Port Already in Use

If port 8000 is busy, use a different port:

```bash
python3 -m http.server 8080
```

Then access at `http://localhost:8080`

### Files Not Loading

- Ensure you're accessing via `http://localhost:8000` (not `file://`)
- Check browser console for errors (F12 → Console)
- Verify all files (`index.html`, `styles.css`, `app.js`) are in the same directory

### CDN Libraries Not Loading

- Check your internet connection
- Verify CDN URLs in browser's Network tab (F12 → Network)
- If offline, you may need to download libraries locally

### PDF Merging Fails

- Check browser console for error messages
- Verify PDF files are not corrupted
- Ensure PDF-lib CDN is loading (check Network tab)

## Next Steps

Once local testing is successful:

1. Review the [DEPLOYMENT.md](DEPLOYMENT.md) guide
2. Commit your changes to Git
3. Push to GitHub
4. Enable GitHub Pages in repository settings
