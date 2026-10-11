# Iyrin installation

Iyrin opens in a dedicated Edge WebView2 window without browser tabs or an address bar. Its existing workflow tabs and controls remain available. Closing the window stops the local Streamlit server.

## Requirements

- Windows x64 with [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).
- Python 3.11 or 3.12 for PyPI installation. The standalone installer includes Python.
- Disk space for scientific, GIS, machine-learning, and browser dependencies.
- Internet access and your own API credentials for services you use. Local models, NLP corpora, and browser binaries may require separate downloads.

## Install from PyPI

After publication, run in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install iyrin-py
iyrin
```

The distribution is `iyrin-py`; the import is `iyrin`. `iyrin` launches the tabless Windows UI. `iyrin-browser` launches browser mode on supported operating systems. Installing llama-cpp-python from source requires Visual Studio Build Tools with Desktop development with C++ on Windows.

## Windows installer

1. Open [Windows installer Actions](https://github.com/is-leeroy-jenkins/Iyrin/actions/workflows/windows-installer.yml) after merging the packaging changes.
2. Run **Build Iyrin Windows desktop installer** on `main`.
3. Download and extract the **Iyrin-Windows-Installer** artifact from the successful run.
4. Run `Iyrin-Setup-0.2.0.exe`, choose the optional desktop shortcut, and finish the wizard.
5. Launch Iyrin from the Start Menu or desktop shortcut.

The default installation is `%LOCALAPPDATA%\Programs\Iyrin`, without administrator privileges. Builds are unsigned unless signing is configured. The workflow uploads an artifact rather than publishing a release automatically.

## Credentials and optional downloads

Configure the environment variables documented in `config.py` and the existing [API setup guide](setup/API-Setup.md). Google Maps/geocoding, weather, provider generation, embeddings, cloud documents, and remote vector stores each require their applicable service credentials. Restart your terminal or sign out and back in after changing persistent environment variables before launching a shortcut. Credentials are not included in the package.

Playwright document loading requires Chromium. For a PyPI installation, install it once in the activated environment:

```powershell
python -m playwright install chromium
```

The Windows installer build includes Chromium for Playwright. Browser files are resolved from the installed bundle by the desktop launcher. Scientific services may download cache data, and Cartopy may download map datasets. NLP features require the selected NLTK corpora or spaCy model; install the datasets/models required by the processing options you use. Sentence-transformer models download separately. Local llama.cpp features require compatible GGUF weights configured through the existing controls. No model weights or credentials are bundled.

## Data and theme

Writable resources, theme settings, databases, exports, and logs use `%LOCALAPPDATA%\Iyrin`. The launcher creates `stores\sqlite`, preserves existing files, and binds Streamlit to `127.0.0.1` on an available port. Custom fonts are included with the package and installer. Development databases, logs, notebooks, secrets, and model weights are excluded.

## Build from source

Install Git, Python 3.11 x64, Visual Studio Build Tools with Desktop development with C++, and [Inno Setup 6](https://jrsoftware.org/isinfo.php). On Windows:

```powershell
git clone https://github.com/is-leeroy-jenkins/Iyrin.git
cd Iyrin
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-desktop.txt
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\browser-binaries"
python -m playwright install chromium
python desktop.py
python -m PyInstaller --noconfirm --clean iyrin.spec
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer\iyrin.iss"
```

The Setup executable is written to `dist-installer`. Build on Windows; PyInstaller does not cross-compile Windows executables from Linux.

## Troubleshooting, upgrades, and uninstall

Check `%LOCALAPPDATA%\Iyrin\desktop.log` for startup errors. Install WebView2 if the window does not open. For service failures, verify credentials and connectivity. For NLP or browser-loading failures, verify optional downloads.

Close Iyrin and back up `%LOCALAPPDATA%\Iyrin` before upgrading. Uninstall through Windows Settings → Apps → Iyrin. User data remains and can be removed separately.

Validate the native build on Windows: startup, custom fonts, representative map/loading/processing/vector operations, Playwright loading, persistence, server cleanup on close, and uninstall.

[PyPI release instructions](pypi-release.md) · [README](../README.md)
