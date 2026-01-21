# Building PDF Batch Merger

This guide explains how to build the desktop application from source.

## Prerequisites

1. Python 3.8 or higher
2. All dependencies from `requirements.txt`
3. PyInstaller (included in requirements)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate License Keys

Before building, you need to generate RSA keys for license signing:

```bash
python tools/license_generator.py generate-keys --output-dir tools
```

This creates:
- `tools/private_key.pem` - Keep this secret! Use it to sign licenses
- `tools/public_key.pem` - Embed this in the app

### 3. Embed Public Key

Copy the public key to the licensing module:

```bash
cp tools/public_key.pem pdf_merger/licensing/public_key.pem
```

**Important**: The public key will be included in the packaged application. The private key should NEVER be included.

## Building

### macOS

```bash
./build_config/build.sh
```

The built application will be in `dist/PDF Batch Merger.app`

### Windows

```cmd
build_config\build.bat
```

The built executable will be in `dist/PDF Batch Merger.exe`

## Manual Build (Alternative)

If the build scripts don't work, you can build manually:

### macOS

```bash
pyinstaller build_config/macos.spec
```

### Windows

```bash
pyinstaller build_config/windows.spec
```

## Testing the Build

### macOS

```bash
open "dist/PDF Batch Merger.app"
```

### Windows

```cmd
dist\PDF Batch Merger.exe
```

**Important**: Test on a clean machine (or VM) without Python installed to ensure all dependencies are bundled correctly.

## Distribution Package

Create a distribution package with:

1. The built application (`.app` or `.exe`)
2. A sample `license.json` (or provide separately)
3. `README.pdf` (convert `docs/README_USER.md` to PDF)
4. A sample input file (`sample_input.xlsx`)

Example structure:

```
PDF_Batch_Merger/
├── PDF Batch Merger.app (or .exe)
├── license.json (provided separately to clients)
├── README.pdf
└── sample_input.xlsx
```

## Troubleshooting

### "Public key not found" error

- Make sure you've copied `tools/public_key.pem` to `pdf_merger/licensing/public_key.pem`
- Rebuild the application after adding the public key

### Application won't start

- Check that all dependencies are installed
- Try running from source first: `python main.py`
- Check the console for error messages (if console=True in spec file)

### Missing modules in packaged app

- Add missing modules to `hiddenimports` in the `.spec` file
- Rebuild the application

## License Generation

See `tools/README.md` for instructions on generating licenses for clients.
