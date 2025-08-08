# How to Remove **Release Drafter** from Your GitHub Repository

**Release Drafter** is a GitHub Action/app that helps automate release note generation. If you’ve used it before but now want to switch to GitHub’s built-in release notes or just remove it from your workflow, follow these steps to “surgically” remove Release Drafter from your repository.

---

## 1. Delete Workflow and Config Files

Release Drafter uses two files in your repo:

* `.github/workflows/release-drafter.yml` (the workflow)
* `.github/release-drafter.yml` (the config)

**Delete both files.**

You can do this via your file explorer or with a command:

```sh
rm .github/release-drafter.yml .github/workflows/release-drafter.yml
```

---

## 2. (Optional) Remove References in Documentation

* Update or remove any mention of “Release Drafter” in your `README.md` or other project docs.

---

## 3. Commit Your Changes

**Suggested commit message:**

```
chore: remove Release Drafter workflow and config
```

---

## 4. Push to Your Repository

```sh
git add .github/release-drafter.yml .github/workflows/release-drafter.yml
git commit -m "chore: remove Release Drafter workflow and config"
git push
```

---

## 5. (Optional) Remove GitHub App Integration

If you installed the Release Drafter GitHub App, go to [GitHub App settings](https://github.com/settings/installations), find Release Drafter, and uninstall it from your repo or org.

---

## 6. Verify Removal

* Ensure the workflow is gone from the Actions tab.
* Confirm new releases no longer mention Release Drafter.
* Use GitHub’s built-in “Generate release notes” button to test default release notes.

---

**You have now fully removed Release Drafter.**
GitHub’s built-in release notes are available by default.
