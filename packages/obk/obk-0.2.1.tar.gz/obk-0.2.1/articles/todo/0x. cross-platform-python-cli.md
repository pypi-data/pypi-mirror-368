# How to Write a Cross-Platform Python CLI with Platform-Specific Backends

**Python is famous for its cross-platform support, but what if you need your CLI tool to handle OS-specific logic behind the scenes?** This guide will show you how to build a CLI that exposes a consistent interface to the user, but runs platform-specific code under the hood—perfect for tools that need to interact with the operating system in different ways on Windows, macOS, or Linux.

* * *

## 1. **Why Bother with Platform Abstraction?**

* **Consistent UX:**  
    Users get the _same_ commands and output, regardless of their OS.
    
* **Maximum Compatibility:**  
    Handle quirks or missing features on some platforms without breaking the CLI for others.
    
* **Easy Maintenance:**  
    Add new OS support or features without changing your main codebase.
    

* * *

## 2. **Basic Design Pattern**

* **Step 1:** Expose a unified interface—functions or classes that your CLI code uses.
    
* **Step 2:** Under the hood, detect the current platform.
    
* **Step 3:** Delegate to platform-specific implementations as needed.
    

* * *

## 3. **Detecting the Platform**

Python’s `platform` module lets you easily identify the OS:

```python
import platform

system = platform.system()
print(system)  # Outputs: "Windows", "Linux", or "Darwin" (for macOS)
```

* * *

## 4. **Defining the Unified Interface**

Suppose you want to list files in a directory, but want to use native commands on each OS.

**First, define a base interface:**

```python
class FileSystemHelper:
    def list_files(self, path):
        raise NotImplementedError
```

* * *

## 5. **Implementing Platform-Specific Backends**

**For Windows:**

```python
import subprocess

class WindowsFileSystemHelper(FileSystemHelper):
    def list_files(self, path):
        result = subprocess.run(
            ["powershell", "-Command", f"Get-ChildItem -Path '{path}' | Select-Object -ExpandProperty Name"],
            capture_output=True,
            text=True
        )
        return result.stdout.splitlines()
```

**For Unix (Linux/macOS):**

```python
class UnixFileSystemHelper(FileSystemHelper):
    def list_files(self, path):
        result = subprocess.run(
            ["ls", path],
            capture_output=True,
            text=True
        )
        return result.stdout.splitlines()
```

* * *

## 6. **Factory for the Right Implementation**

Choose the correct backend at runtime:

```python
def get_filesystem_helper():
    import platform
    if platform.system() == "Windows":
        return WindowsFileSystemHelper()
    else:
        return UnixFileSystemHelper()
```

* * *

## 7. **Using the Helper in Your CLI**

Now your CLI code doesn’t care about the OS—it just calls the helper:

```python
helper = get_filesystem_helper()
files = helper.list_files(".")
for f in files:
    print(f)
```

* * *

## 8. **Best Practice: Prefer Python’s Cross-Platform APIs!**

> For most file operations, Python’s standard library (`os`, `shutil`, `pathlib`) is already cross-platform.  
> Use native commands or OS-specific code _only when you must_ (e.g., registry editing, package managers, system services).

* * *

## 9. **Scaling Up**

* Add more methods to `FileSystemHelper` for other OS tasks.
    
* Implement additional OS-specific classes as needed (e.g., `MacOSFileSystemHelper` if macOS differs from Linux).
    
* Use dependency injection or factories for even more flexibility and testability.
    

* * *

## 10. **Summary**

* **You can easily write a Python CLI that works everywhere, but uses the “right tool” for each OS.**
    
* **Expose a unified interface, detect the platform at runtime, and delegate to platform-specific logic as needed.**
    
* **Stick with Python’s built-in cross-platform libraries for most tasks, and go native only when necessary.**
    

* * *

**Ready to make your CLI robust and user-friendly—no matter what platform it runs on? Now you know how!**

* * *

**Need a more complex example, or want help wiring this into your actual project? Just ask!**

* * *

## 11. **Bonus: Using Dependency Injection Instead of Factories**

Dependency Injection (DI) makes it easier to manage dependencies, swap implementations, and write testable code—especially as your project grows. With the `dependency-injector` library, you can cleanly inject platform-specific helpers into your CLI with minimal code changes.

### **A. Install dependency-injector**

```bash
pip install dependency-injector
```

* * *

### **B. Define Your Helpers (No Changes Needed)**

Keep your `FileSystemHelper`, `WindowsFileSystemHelper`, and `UnixFileSystemHelper` classes as shown above.

* * *

### **C. Create a DI Container for Platform Binding**

```python
from dependency_injector import containers, providers
import platform

class Container(containers.DeclarativeContainer):
    if platform.system() == "Windows":
        filesystem_helper = providers.Singleton(WindowsFileSystemHelper)
    else:
        filesystem_helper = providers.Singleton(UnixFileSystemHelper)
```

* * *

### **D. Use the Injected Dependency in Your CLI**

```python
# main.py
from containers import Container

def main():
    container = Container()
    helper = container.filesystem_helper()
    files = helper.list_files(".")
    for f in files:
        print(f)

if __name__ == "__main__":
    main()
```

* * *

### **E. Benefits of the DI Approach**

* **Cleaner separation:** You never instantiate OS-specific classes directly in your CLI code.
    
* **Easy to override for testing:** In your test setup, just override the provider:
    
    ```python
    container.filesystem_helper.override(MockFileSystemHelper())
    ```
    
* **Scalability:** Add new backends or dependencies (logging, config, etc.) without changing your main logic.
    

* * *

**With dependency injection, your CLI stays clean, testable, and ready for future expansion—no more manual factory logic needed!**

* * *

## 12. **Project Scaffold: Cross-Platform CLI with Dependency Injection and Useful Commands**

Below is a full project structure and sample code for a cross-platform CLI tool with DI.  
**The CLI includes three very useful commands:**

* `list-files`: List files in a directory
    
* `file-info`: Show detailed info for a file
    
* `disk-free`: Display free disk space
    

**All commands work cross-platform, but implementation can be customized per OS.**

* * *

### **Project Structure**

```
yourcli/
├── cli.py
├── containers.py
├── filesystem.py
├── requirements.txt
└── README.md
```

* * *

### **filesystem.py**

_Define your abstract helper and implementations:_

```python
import os
import platform
import subprocess
from abc import ABC, abstractmethod

class FileSystemHelper(ABC):
    @abstractmethod
    def list_files(self, path):
        pass

    @abstractmethod
    def file_info(self, path):
        pass

    @abstractmethod
    def disk_free(self, path):
        pass

class WindowsFileSystemHelper(FileSystemHelper):
    def list_files(self, path):
        result = subprocess.run(
            ["powershell", "-Command", f"Get-ChildItem -Path '{path}' | Select-Object -ExpandProperty Name"],
            capture_output=True,
            text=True
        )
        return result.stdout.splitlines()

    def file_info(self, path):
        result = subprocess.run(
            ["powershell", "-Command", f"Get-Item '{path}' | Format-List *"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def disk_free(self, path):
        result = subprocess.run(
            ["powershell", "-Command", f"Get-PSDrive -Name (Get-Item '{path}').PSDrive.Name | Select-Object Used,Free"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

class UnixFileSystemHelper(FileSystemHelper):
    def list_files(self, path):
        return os.listdir(path)

    def file_info(self, path):
        stat = os.stat(path)
        return (
            f"Path: {path}\n"
            f"Size: {stat.st_size} bytes\n"
            f"Permissions: {oct(stat.st_mode)}\n"
            f"Owner: {stat.st_uid}:{stat.st_gid}\n"
            f"Last modified: {stat.st_mtime}\n"
        )

    def disk_free(self, path):
        statvfs = os.statvfs(path)
        free = statvfs.f_frsize * statvfs.f_bavail
        total = statvfs.f_frsize * statvfs.f_blocks
        return f"Free: {free // (1024 * 1024)} MB / Total: {total // (1024 * 1024)} MB"

```

* * *

### **containers.py**

_Set up your dependency injector container:_

```python
from dependency_injector import containers, providers
import platform
from filesystem import WindowsFileSystemHelper, UnixFileSystemHelper

class Container(containers.DeclarativeContainer):
    if platform.system() == "Windows":
        filesystem_helper = providers.Singleton(WindowsFileSystemHelper)
    else:
        filesystem_helper = providers.Singleton(UnixFileSystemHelper)
```

* * *

### **cli.py**

_Define your CLI using Click (or Typer):_

```python
import click
from containers import Container

container = Container()
fs = container.filesystem_helper()

@click.group()
def cli():
    """Cross-platform CLI Tool!"""
    pass

@cli.command()
@click.argument('path', default='.')
def list_files(path):
    """List files in a directory."""
    files = fs.list_files(path)
    for f in files:
        print(f)

@cli.command()
@click.argument('path')
def file_info(path):
    """Show detailed info for a file."""
    print(fs.file_info(path))

@cli.command()
@click.argument('path', default='.')
def disk_free(path):
    """Display free disk space for the given path."""
    print(fs.disk_free(path))

if __name__ == '__main__':
    cli()
```

* * *

### **requirements.txt**

```
dependency-injector
click
```

* * *

### **README.md**

(Add a simple README for usage.)

```markdown
# YourCLI

A cross-platform command-line tool for basic filesystem tasks, powered by dependency injection.

## Installation

```

pip install -r requirements.txt

```

## Usage

```

python cli.py list-files .  
python cli.py file-info myfile.txt  
python cli.py disk-free /

```
```

* * *

## **You now have:**

* A cross-platform, DI-powered Python CLI scaffold
    
* Useful, real-world commands
    
* Clean separation between interface and platform-specific logic
    
* A foundation you can grow and test
    