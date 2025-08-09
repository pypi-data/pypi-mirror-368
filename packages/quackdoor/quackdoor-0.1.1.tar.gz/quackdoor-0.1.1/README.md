# 🦆 Quackdoor

![CI](https://github.com/mah5057/quackdoor/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/mah5057/quackdoor/branch/main/graph/badge.svg)](https://codecov.io/gh/mah5057/quackdoor)

**Honk Honk!**  
Quackdoor is a CLI tool written in Python that generates DuckyScript to execute arbitrary Python code on a target machine. It is best used for crafting payloads for [Flipper Zero's BadUSB](https://docs.flipperzero.one/badusb) app.

---

## 🔧 Features

- Embeds Python scripts into an executable DuckyScript
- Supports external Python libraries (via `-r` and `-p` flags)
- Tailored for use with macOS and Zsh environments
- Ideal for authorized security testing and educational purposes

---

## ⚠️ Limitations & Considerations

- The target system **must have Python 3** installed
- All local Python code must reside in **a single file**; other local modules will not be compiled into the payload
- **External libraries are supported** and will be installed globally on the target via pip
- Payload may leave **recoverable traces** on the target system—use with caution
- Assumes the **Zsh shell** and **standard macOS filesystem** on the target

---

## 🚀 Getting Started

Clone the repository:

```zsh
git clone https://github.com/your-org/quackdoor.git
```

Generate a payload:

```zsh
cd quackdoor
python3 quackdoor.py -i your_script.py -o output_file_name.txt
```

Optional flags for additional customization:
- `-r dependency1 dependency2` – Provide a space delimited list of dependencies to install
- `-p` – Pip-time, or how long for the resulting DuckyScript to wait after running pip install (if there are dependencies provided)

---

## ✅ Development Best Practices

We follow the **GitHub Flow** for all development work:

1. Create a new branch from `main`:
   ```zsh
   git checkout -b feature/my-feature
   ```

2. Make your changes and commit them:
   ```zsh
   git commit -m "#123 Brief description of the change"
   ```

   - Always reference the GitHub issue number with a `#`, e.g. `#42`
   - Write clear and descriptive commit messages

3. Push your branch:
   ```zsh
   git push origin feature/my-feature
   ```

4. Open a Pull Request targeting the `main` branch

5. Request review and ensure all checks pass

6. Once approved, squash and merge

---

📦 Release Process

1. Bump the version in pyproject.toml
2. Edit the version field to the new release number:

```toml
version = "0.1.1"
```
Commit the change:
```zsh
git add pyproject.toml
git commit -m "Bump version to 0.1.1"
```

3. Tag the release
Tag should match the version in pyproject.toml exactly, prefixed with v:
```zsh
git tag v0.1.1
git push origin v0.1.1
```

Create the GitHub Release

1. Go to the GitHub "Releases" page

2. Click "Draft a new release"

3. Select the tag you just pushed

4. Fill in release notes. Include a changelog with a compare url like:

```zsh
https://github.com/mah5057/quackdoor/compare/v0.1.0...v0.1.1
```

5. Click "Publish release"

Publishing to PyPI

The CI workflow will automatically build and publish the new version to PyPI once the GitHub release is published.



---

## 📄 License

MIT License. See [LICENSE](./LICENSE) for details.

---

## 🛡️ Disclaimer

This software is provided for **educational and authorized testing purposes only**.  
The author is not responsible for **misuse, damage, or legal consequences** resulting from the use of this tool.

Use responsibly. Honk responsibly. 🦆
