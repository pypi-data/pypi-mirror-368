# gcil

## Test on Linux

The following tools are required for Linux hosts tests (example: Linux Mint, Ubuntu, CentOS, ...):

- **PyPI :** <https://pip.pypa.io/en/stable/installing/>
- **gitlabci-local :** `pipx install --force gitlabci-local`

The following engines are available:

- **Docker :** <https://docs.docker.com/engine/install/>
- **Podman :** <https://podman.io/getting-started/installation#linux-distributions>

---

## Test on macOS

The following tools are required for macOS hosts tests (example: 10.14, 10.15, 11.0, ...):

- **Python :** Type `python3` in the Terminal app and install automatically
- **gitlabci-local :** `pip3 install -U gitlabci-local`

The following engines are available:

- **Docker :** <https://docs.docker.com/engine/install/>

---

## Test on Windows

The following tools are required for Windows 10 hosts tests (example: 1909, 2004, 20H2, ...):

- **Git for Windows :** <https://gitforwindows.org> (Git, 64-bit.exe)
- **Python :** <https://www.python.org/downloads/windows/> (Python 3, x86-64 executable, all users, add to PATH, path length limit disabled)
- **gitlabci-local :** `pip3 install -U gitlabci-local`

The following hypervisors are available:

- **Hyper-V :** <https://docs.microsoft.com/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v>
- **WSL 2 :** <https://docs.microsoft.com/windows/wsl/install-win10>

The following engines are available:

- **Docker :** <https://docs.docker.com/docker-for-windows/install/> (Docker Desktop)

---

## Test on Android

The following tools are required for Android hosts tests (example: 11, 10, ...):

- **Termux :** Install the `Termux` application (<https://termux.com>)
- **OpenSSL :** Type `pkg install openssl` in the Termux app
- **Python :** Type `pkg install python` in the Termux app
- **pip :** Type `python3 -m pip install -U pip` in the Termux app
- **gitlabci-local :** `pip3 install -U gitlabci-local`
