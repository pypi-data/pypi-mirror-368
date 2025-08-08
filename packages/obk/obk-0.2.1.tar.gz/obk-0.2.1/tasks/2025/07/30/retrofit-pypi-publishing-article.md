## [Refactor Task] Retrofit PyPI Publishing Article for `obk`

**Objective:**  
Update `publish-a-package-to-pypi.md` so that its instructions and details accurately reflect the current structure and workflow of `obk`. All changes must be delivered as a single, unified change set.

* * *

### 1. Repository Analysis

* Analyze `obk` to understand:
    
    * Source layout, module/package naming, and entry points.
        
    * Build and publish process (tools, files, commands).
        
    * Dependency management system in use.
        
    * Any relevant CI/CD or automation that affects publishing.
        

* * *

### 2. Article Extraction & Update

* Review the existing `publish-a-package-to-pypi.md`.
    
* Update:
    
    * All paths, names, and commands to match this repo.
        
    * Any generic or outdated guidance to be project-specific.
        
    * Steps to include/exclude only what’s relevant for this codebase.
        
    * Terminology and structure to match repo conventions.
        

* * *

### 3. Verification (Manual/Test)

* Confirm the new instructions work end-to-end by referencing actual repo state. (No code/test changes required, but ensure the doc can be followed verbatim.)
    
* (Optional) Add a short “How to test these instructions” note at the end of the article.
    

* * *

### 4. Modification Policy

**Allowed file changes:**

* `publish-a-package-to-pypi.md` (mandatory)
    

**Prohibited:**

* All other files must remain unchanged.
    

* * *

**Instructions:**

* Follow each step in order.
    
* Output all changes as a single commit.
    


* * *