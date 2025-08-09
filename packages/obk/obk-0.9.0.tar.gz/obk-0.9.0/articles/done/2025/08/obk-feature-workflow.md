# **OBK Feature Workflow**

* * *

## **Overview**

This document describes the standard workflow for developing and integrating new features in OBK, using a simplified, tag-triggered deployment process.  
All development is done in feature branches based on `main`, and releases are handled exclusively via semantic version tags that match your `pyproject.toml`.

* * *

## **Feature Development Workflow**

### **1. Branch from `main`**

* Create your feature branch directly from `main`.
    
    * **Example:**
        
        ```bash
        git checkout main
        git pull
        git checkout -b your-feature-name
        ```
        
* No required naming conventions (but using a `feature/` prefix is fine if you like).
    

* * *

### **2. Make Your Changes**

* Commit code, tests, and documentation as needed.
    
* Regularly pull/rebase from `main` to stay up to date.
    

* * *

### **3. Open a Pull Request to `main`**

* When your feature is ready, open a PR against `main`.
    
* **Squash** and merge when ready:
    
    * All changes should be squashed into a single commit (or a tidy set if needed for clarity).
        
* Passing CI is required before merge.
    

* * *

### **4. Version Bumping**

* **Do not** bump the version until the release is actually being prepared.
    
* Feature branches and PRs should leave `pyproject.toml` at the current released version.
    
* **Only when the feature(s) are ready for release:**
    
    * Bump the version in `pyproject.toml` to the next intended version (e.g., `1.3.0`).
        
    * Include the version bump as the **very last, squashed commit to `main`** before tagging.
        

* * *

### **5. Release Preparation (if applicable)**

* After merging all features for a release, update documentation and changelog as needed.
    
* Ensure all code and versioning is ready on `main`.
    

* * *

### **6. Create a Release Tag**

* On GitHub (or via git), create a tag matching the new version:
    
    * **Format:** `vX.Y.Z` (e.g., `v1.3.0`)
        
* Push the tag to the repo.
    
* **This tag is what triggers the deployment workflow.**
    

* * *

### **7. Deployment**

* The CI/CD pipeline will:
    
    * Validate that the `pyproject.toml` version matches the tag.
        
    * Build and test your package.
        
    * Deploy to PyPI **only if** the versions match.
        
* If there’s a mismatch, the workflow fails and nothing is deployed.
    

* * *

## **Summary Checklist**

*  Branch from `main`
    
*  Commit and test your changes
    
*  PR and squash merge to `main`
    
*  Bump `pyproject.toml` version **as the last commit before tagging**
    
*  Merge version bump to `main`
    
*  Create and push matching tag (e.g., `v1.3.0`)
    
*  CI/CD validates and (if matching) deploys to PyPI
    

* * *

## **Best Practices**

* **Never bump the version at the start of a feature.** Only bump at the final release step.
    
* **Do not use commit-message deploy triggers** (`[patch]`, `[minor]`, etc.)—all deploys are tag-based.
    
* **Branch names are flexible.** Use what works for your team.
    

* * *

## **FAQ**

**Q: Can I work on multiple features before releasing?**  
A: Yes—squash-merge each feature to `main`. Bump the version and create a tag only when ready to release.

**Q: What if I forget to bump the version before tagging?**  
A: The workflow will fail and warn you. Just bump the version in `pyproject.toml`, merge, and re-tag.

**Q: What if two features are ready at once?**  
A: Merge both to `main`, then bump the version and release together.

* * *

## **References**

* [How to Implement Tag-Triggered Deployments](#) <!-- Link to your article or prompt as needed -->
    
* [OBK Hotfix Workflow](obk-hotfix-workflow.md)
    
* [OBK Release Workflow](obk-release-workflow.md)
    

* * *