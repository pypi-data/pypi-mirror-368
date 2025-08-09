# Troubleshooting: `'obk' is not recognized as a command after pip install`

After running `pip install obk`, some users on Windows (and occasionally Mac/Linux) may find that the `obk` command is **not recognized** in their terminal or command prompt. This article explains why this happens and how to fix it.

* * *

## Why Doesn’t the `obk` Command Work?

When you install a Python CLI tool via pip, it tries to create an executable script (`obk`) in your **Python Scripts directory**. This directory must be present in your system’s `PATH` for your shell to recognize the `obk` command.

**Common reasons the command isn’t found:**

* Your terminal hasn’t picked up recent changes to your PATH (e.g., you haven’t restarted the terminal).
    
* The Python Scripts directory is not included in your PATH environment variable.
    
* There were permission or environment issues during installation.
    

* * *

## Solutions

### 1. Try Restarting Your Terminal

* Close your terminal (or Command Prompt, or PowerShell).
    
* Open it again, and try running:
    
    ```
    obk --help
    ```
    
* If it still doesn’t work, continue below.
    

* * *

### 2. Find Your Python Scripts Directory

You need to find where pip installed the `obk` script.

**On Windows**, common locations are:

* For system installs:  
    `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python3x\Scripts\`
    
* For user installs:  
    `C:\Users\<YourUsername>\AppData\Roaming\Python\Python3x\Scripts\`
    
* Or, as in your error:  
    `C:\Users\<YourUsername>\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\`
    

**On macOS/Linux**, it’s usually:

* `~/.local/bin/`
    
* Or within your virtual environment, if using one
    

* * *

### 3. Add the Scripts Directory to Your PATH

#### Windows

1. Copy the path to your Scripts directory (see above).
    
2. Open the Start menu, search for **Environment Variables**, and select **Edit the system environment variables**.
    
3. Click **Environment Variables…**
    
4. In **User variables** (or **System variables**), find and select `Path`, then click **Edit**.
    
5. **Add a new entry** for your Scripts directory.
    
6. Click OK and restart your terminal.
    

#### macOS/Linux

Add this line to your `~/.bashrc`, `~/.zshrc`, or similar:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

Then run:

```sh
source ~/.bashrc    # or source ~/.zshrc
```

* * *

### 4. (Alternative) Run with `python -m obk`

If you still can’t get the `obk` command to work, you can always use:

```sh
python -m obk --help
```

This will run OBK using Python directly.

* * *

## Summary Table

| Issue | Solution |
| --- | --- |
| Command not found | Restart terminal |
| Scripts dir not in PATH | Add Scripts dir to PATH |
| Still doesn’t work | Use `python -m obk` |

* * *

## When to Contact Support

If you’ve tried all the above and still can’t run `obk`, please [open an issue on GitHub](https://github.com/bynbb/obk/issues) with the following information:

* Your OS (Windows/Mac/Linux)
    
* Your Python version
    
* Output of `pip show obk`
    
* Output of `echo %PATH%` (Windows) or `echo $PATH` (Mac/Linux)
    

* * *

## References

* pip documentation: User Guide – Scripts
    
* Python Packaging Authority: Entry Points
    

* * *

**Need help? [Open an issue!](https://github.com/bynbb/obk/issues)**

* * *