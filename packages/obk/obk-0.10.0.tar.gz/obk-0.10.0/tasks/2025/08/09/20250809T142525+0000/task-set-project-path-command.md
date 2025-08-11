## **Task: Implement `set-project-path` Feature and Remove Legacy Walk-up Logic**

### **Objective**

Implement a new CLI command `set-project-path` that explicitly manages the project root path for all prompt-based commands in the `obk` CLI, replacing the deprecated “walk up” search entirely. 


### **Implementation Steps**

#### 1. **Add `set-project-path` Command**

* Add a new Typer command in the CLI:
    
    * `--path <dir>` — set an explicit project root.
        
    * `--here` — set project root to the current working directory.
        
    * `--unset` — clear the stored project root.
        
    * `--show` — display the effective project root and where it was sourced from (env/config).
        

#### 2. **Implement Config Storage**

* Store `project_path` in:
    
    * Linux/macOS: `~/.config/obk/config.toml`
        
    * Windows: `%APPDATA%\obk\config.toml`
        
* Use `platformdirs` if available, or manually determine the platform-specific config dir.
    
* Store in TOML format.
    

#### 3. **Implement `resolve_project_root()`**

* Resolution precedence:
    
    1. `OBK_PROJECT_PATH` environment variable.
        
    2. Value from `config.toml`.
        
    3. **No fallback** — if neither is set, exit with:
        
        ```
        ❌ No project path configured. Run `obk set-project-path --here` or use --path <dir>.
        ```
        
        and exit with a non-zero status code.
        
* This function will replace all calls to the old `find_prompts_root()`.
    

#### 4. **Remove Legacy Walk-up Search**

* Delete all code that searches parent directories for a `prompts/` folder.
    
* Remove associated tests for walk-up search behavior.
    

#### 5. **Update Existing Commands**

* `validate-all`, `harmonize-all`, and any other commands that use prompt files must:
    
    * Call `resolve_project_root()` at the start.
        
    * Use the returned path for locating prompts.
        

* * *

### **Testing Requirements**

* Add `pytest` tests covering:
    
    * Setting project path via `--path`.
        
    * Setting project path via `--here`.
        
    * Clearing with `--unset`.
        
    * Showing with `--show`.
        
    * Env var precedence over config file.
        
    * Error message when unset.
        
    * Behavior verified on both Linux/macOS and Windows paths (simulate Windows paths in tests).
        

* * *

### **Deliverables**

* Updated CLI source files with `set-project-path` and `resolve_project_root()`.
    
* Removal of walk-up logic from all modules.
    
* New tests in the `tests/` folder.
    
* All existing tests pass.
    
* Code packaged in a zip for deployment.
    

* * *