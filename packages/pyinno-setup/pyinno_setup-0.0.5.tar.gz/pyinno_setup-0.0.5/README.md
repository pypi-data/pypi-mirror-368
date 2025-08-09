
## 🚀 pyinno_setup
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Issues](https://img.shields.io/github/issues/its-me-abi/pyinno_setup.svg)](https://github.com/its-me-abi/pyinno_setup/issues)

it is an python wrapper for programmatically building installable exe from iss script using embedded innosetup binary.  


### ✨ Features

- **Automate Installer Creation:** Generate Windows installers (`.exe`) from Python without comandline or gui,
- **Seamless Inno Setup Integration:** Harness the full power of Inno Setup, embedded and ready to use.

### 📦 Installation
from pypi using pip
```
pip install pyinno-setup
```
from github source:
```
git clone https://github.com/its-me-abi/pyinno_setup.git

```

### 🛠️ Quick Start

```python
from pyinno_setup import inno

if inno.build("inputfolder/template.iss", "outfolder"):
    print("### successfully built")
else:
    print("### build failed ")
```

another example using class

```
    setup = inno.setup ( "inputfolder/template.iss", outfolder = "outfolder" , outfile="xxx" )
    print("cli arguemnts are " , setup.get_cli_list())
    try:
        if setup.build():
            print("### successfully built by innosetup ###")
    except:
        print("### innosetup build failed ###")

```

### 💡 Why pyinno_setup?

- **No more manual ` cli or gui .**
- no need to install and configure innosetup yourself,everything is avaialble in this package
---

### 🖥️ Requirements

- Python 3.6+
- [Inno Setup](https://jrsoftware.org/isinfo.php) (embedded or available in your environment)
- Windows OS needed because innosetup only works in windows and it is for windows

---

### 🤝 Contributing

1. Fork this repo
2. Create a feature branch (`git checkout -b awesome-feature`)
3. Commit your changes
4. Open a Pull Request

---

### 📄 License

MIT License. See [LICENSE](LICENSE).

---

### 🙏 Acknowledgements

- [Inno Setup](https://jrsoftware.org/isinfo.php) by Jordan Russell

---

### 🌐 Links

- [wiki](https://github.com/its-me-abi/pyinno_setup/wiki)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/index.php)
