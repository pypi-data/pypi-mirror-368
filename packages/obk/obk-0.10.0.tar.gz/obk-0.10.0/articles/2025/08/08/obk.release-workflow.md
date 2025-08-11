
# **OBK Release Workflow**

* * *

## **Overview**

This guide covers the end-to-end process for preparing, reviewing, and deploying official OBK releases.  
Releases are built from the `main` branch, and deployments to PyPI are triggered by creating a version tag that matches your `pyproject.toml`.  
This workflow ensures every release is intentional, reproducible, and fully automated—no more manual deploys or ambiguous triggers.

* * *

## **Release Workflow**

### **1. Prepare `main` for Release**

* Ensure all planned features and hotfixes have been merged to `main` via squash merges.
    
* Update documentation, changelog, and any user-facing materials as needed.
    
* Run all tests and ensure CI passes on `main`.
    

* * *

### **2. Bump the Version in `pyproject.toml`**

* Edit `pyproject.toml` to set the new release version (e.g., from `1.3.1` to `1.4.0`).
    
* Commit this as the **very last, squashed commit** before tagging the release.
    

* * *

### **3. Merge the Version Bump to `main`**

* Open a PR if you are working in a branch, or commit directly if allowed.
    
* Confirm the version bump is the only change in this commit.
    
* Once merged, verify that `main` now contains the correct version.
    

* * *

### **4. Create and Push a Release Tag**

* Create a Git tag that exactly matches the new version (format: `vX.Y.Z`, e.g., `v1.4.0`).
    
* Push the tag to the repository:
    
    ```bash
    git tag v1.4.0
    git push origin v1.4.0
    ```
    
* This tag is what triggers the deployment workflow in CI/CD.
    

* * *

### **5. Deployment**

* The pipeline will:
    
    * Validate that the `pyproject.toml` version matches the tag.
        
    * Build, test, and upload the package to PyPI if the validation passes.
        
* If the versions do **not** match, the deploy job will fail and nothing is published.
    

* * *

## **Release Checklist**

*  All code and docs merged to `main`
    
*  All tests passing on `main`
    
*  Version bumped in `pyproject.toml` as last squashed commit
    
*  Version bump merged to `main`
    
*  Release tag (`vX.Y.Z`) created and pushed
    
*  CI/CD validates and deploys to PyPI
    

* * *

## **Best Practices**

* **Tag only after confirming code and version are final.**
    
* **Never tag a commit where the version in `pyproject.toml` does not match the tag.**
    
* **Never deploy from a branch or unreviewed commit—always from `main`.**
    
* **Do not use commit-message triggers for deploys.**
    
* Use the release checklist above for every deploy.
    

* * *

## **FAQ**

**Q: What if the deploy fails with a version mismatch?**  
A: Bump the version in `pyproject.toml`, merge to `main`, and re-tag with the correct version.

**Q: Can I include multiple features/fixes in one release?**  
A: Yes. Merge them all to `main`, bump the version, and release as a set.

**Q: Can I make a release without a version bump?**  
A: No. The workflow requires the tag and `pyproject.toml` version to match. Every release must have a unique version.

* * *

## **References**

* [OBK Feature Workflow](obk-feature-workflow.md)
    
* [OBK Hotfix Workflow](obk-hotfix-workflow.md)
    
* [Tag-Triggered Deploy Article](#)
    

* * *