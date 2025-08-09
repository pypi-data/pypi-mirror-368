# Prompt Template 

This article provides a ready-to-use template for creating consistent, maintainable prompt files for **any structured GSL-based workflow**—including but not limited to Codex agent automation.

Each section is commented for clarity. Simply fill in the placeholders to match your specific task.

This template uses GSL elements for reportability and traceability, whether or not Codex agent automation is involved.

---

```xml

<?xml version="1.0" encoding="UTF-8"?>
<gsl-prompt id="<!-- PROMPT_ID_HERE -->" type="<!-- PROMPT_TYPE_VIA_CONVENTIONAL_COMMIT_TAG_HERE -->">
<gsl-header>
    
# <!-- Title for this prompt/task, e.g., "Add Feature X" -->
</gsl-header>
<gsl-block>

<gsl-purpose>
<gsl-label>

## 1. Purpose    
</gsl-label>    
<gsl-description>

<!-- Describe the high-level objective for this prompt, e.g., "Implement feature Y in project Z." -->
</gsl-description>
</gsl-purpose>

<gsl-inputs>
<gsl-label>
    
## 2. Inputs
</gsl-label>
<gsl-description>

<!-- List key tools, articles, or other input artifacts that guide the prompt. -->
| Input | Notes |
| --- | --- |
| <!-- Tool/Article/Config --> | <!-- Short description --> |
| <!-- Example: ChatGPT / Codex --> | Tool |
| <!-- Example: "How to Write One-Line Manual Tests" --> | Article |

</gsl-description>
</gsl-inputs>

<gsl-outputs>
<gsl-label>

## 3. Outputs
</gsl-label>
<gsl-description>

<!-- List main components or deliverables produced by this prompt. -->
- <!-- Example: Updated CLI command -->
- <!-- Example: Test suite covering new functionality -->

</gsl-description>
</gsl-outputs>

<gsl-workflows>
<gsl-label>

## 4. Workflows
</gsl-label>
<gsl-description>

<!-- List main steps or processes required for the task. -->
- <!-- Example: Install dependencies -->
- <!-- Example: Refactor module_x.py to use classes -->
- <!-- Example: Update README.md -->

</gsl-description>
</gsl-workflows>
<gsl-acceptance-tests>
<gsl-label>

## 5. Acceptance Tests
</gsl-label>
<gsl-acceptance-test id="1">
<gsl-performed-action>

1. When I lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed feugiat, urna vitae cursus dictum, est purus cursus enim.
</gsl-performed-action>
<gsl-expected-result>
    Then vivamus blandit massa nec velit faucibus, at ultricies sapien gravida. Pellentesque habitant morbi tristique senectus.
</gsl-expected-result>
</gsl-acceptance-test>

<gsl-acceptance-test id="2">
<gsl-performed-action>

2. When I ut placerat orci nulla, at dictum risus viverra ac. Morbi lacinia, nisi id blandit dictum, felis erat rutrum justo.
</gsl-performed-action>
<gsl-expected-result>
    Then curabitur varius, tellus nec pellentesque ultricies, erat urna tristique elit, nec ultricies urna elit ut lectus.
</gsl-expected-result>
</gsl-acceptance-test>
</gsl-acceptance-tests>

</gsl-block>
</gsl-prompt>

```

---

## How to use:

1. Duplicate this template for each new prompt or when standardizing older ones.
2. Replace all placeholders (`<!-- ... -->`) with your actual content.
3. Keep comments as guidance for maintainers—they can be deleted from finalized prompts if desired.

---