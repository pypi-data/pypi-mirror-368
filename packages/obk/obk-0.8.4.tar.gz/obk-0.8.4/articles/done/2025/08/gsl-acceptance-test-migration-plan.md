# `<gsl-acceptance-test>` Migration Plan

The OBK project has outgrown its legacy `<gsl-test>` structure. Originally designed for simple, often manual test notes, `<gsl-test>` is no longer sufficient for capturing complex behavior, stakeholder expectations, or system correctness in a structured, reviewable way.

This article describes the rationale and step-by-step process for replacing `<gsl-test>` with the new, explicit `<gsl-acceptance-test>` format across the OBK codebase.

---

## What We’re Replacing

### Legacy Format: `<gsl-test>`

`<gsl-test>` was used as a simple, single-line test case entry inside a `<gsl-tdd>` container:

```xml
<gsl-tdd>
  <gsl-test id="T1">obk hello prints greeting</gsl-test>
</gsl-tdd>
```

### Why It Fails

* No distinction between **what is done** and **what is expected**
* No field for linking code or test files
* No way to express test metadata (manual-only, high-risk, etc.)
* Poor automation potential

---

## Introducing `<gsl-acceptance-test>`

The new `<gsl-acceptance-test>` element formalizes acceptance testing in GSL. It introduces required structure and optional metadata to make tests both human-meaningful and automation-friendly.

### Core Features:

* Replaces `<gsl-tdd>` with `<gsl-acceptance-tests>`
* Uses structured child elements:

  * `<gsl-performed-action>` (required)
  * `<gsl-expected-result>` (required)
  * `<gsl-acceptance-criteria>` (optional)
  * `<gsl-filename>` (optional)
* Supports `manual-only="true"` attribute
* Requires `id="..."` attribute

### Example:

```xml
<gsl-acceptance-tests>
  <gsl-acceptance-test id="T3" manual-only="false">
    <gsl-title>Divide by zero raises error</gsl-title>

    <gsl-acceptance-criteria>
      Error message is displayed to console
    </gsl-acceptance-criteria>

    <gsl-performed-action>
      Run: obk divide 4 0
    </gsl-performed-action>

    <gsl-expected-result>
      Error message contains 'Division by zero'
    </gsl-expected-result>

    <gsl-filename>src/obk/commands/divide.py</gsl-filename>
  </gsl-acceptance-test>
</gsl-acceptance-tests>
```

---

## Why Structure Tests This Way?

### 1. Separation of Action and Expectation

* Clearer test intent
* Easier to validate correctness
* Friendly to automation and auditing

### 2. Flexibility of Expression

* Works for BDD, imperative, or exploratory styles

### 3. Visibility of Subjectivity

* Encourages teams to explicitly define expectations

---

## Manual-Only Tests

The `manual-only="true"` attribute allows teams to distinguish tests that are not yet automatable—useful for separating CI responsibilities and identifying future automation targets.

---

## Optional Filename Association

The optional `<gsl-filename>` tag links acceptance tests directly to the relevant source file, test script, or config.

---

## Migration Plan

We now divide the plan into **two phases**: language maintenance and content migration.

---

### **Phase 1 — Update the GSL Infrastructure**

1. **Extend `AGENTS.md` with new element definitions:**

   * Add `<gsl-acceptance-tests>` and `<gsl-acceptance-test>` to the element table.

   * Define the semantics of:

     * `<gsl-performed-action>`

     * `<gsl-expected-result>`

     * `<gsl-acceptance-criteria>`

     * `<gsl-filename>` (if not already present)

2. **Update the GSL XSD schema:**

   * Define the structure of `<gsl-acceptance-tests>` and its child elements.

   * Ensure the 4 **global elements** are allowed (and optional) inside **each non-text element**:

     * `<gsl-label>`

     * `<gsl-title>`

     * `<gsl-description>`

     * `<gsl-value>`

3. **Run validation against sample documents** to confirm the XSD changes are correct and compatible.

4. **Update your harmonization and validation tooling** to support the new elements and container.

---

### **Phase 2 — Migrate Test Content**

5. **Replace `<gsl-tdd>` containers with `<gsl-acceptance-tests>`** in all prompt files.

6. **Replace each `<gsl-test>` element with `<gsl-acceptance-test>`**, using the following mapping strategy:

   * Original test string → `<gsl-performed-action>` and `<gsl-expected-result>` (split/annotate as needed)

   * Optional: infer or add `<gsl-filename>` if obvious

   * Optional: infer or annotate `<gsl-acceptance-criteria>` for high-risk or stakeholder-driven tests

7. **Use Codex/AI assistance for scaffolding**, but **only human authors define expectations.**

8. **Retire any unused `<gsl-test>` usage** and mark legacy `<gsl-tdd>` structures as obsolete in documentation.

---

Replacing `<gsl-test>` with `<gsl-acceptance-test>` turns passive, under-documented test hints into **rich, reviewable, behavioral contracts**. This transition strengthens OBK's testing clarity, trustworthiness, and future automation readiness—and puts meaningful expectations where they belong: in the hands of human authors.
