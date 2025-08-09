# When Manual Exploration Should Precede Automation (and When It Shouldn't)

*— Balancing human judgment with modern automated testing practices.*

---

## Introduction

Traditional Test-Driven Development (TDD) emphasizes manual exploration before automation. Historically, manual, one-line tests provided quick feedback and validated interfaces before committing to automated tests. Today, however, advancements in AI and structured test frameworks have changed the game, enabling automatic test generation without manual precursor steps. This article clarifies when manual exploration is beneficial and when it’s appropriate to rely immediately on automated, AI-driven testing.

---

## Manual Exploration: Still Essential

Manual testing excels in scenarios demanding human intuition, creativity, and judgment.

### Key Scenarios for Manual Exploration:

* **Interface Design and Exploratory Prototyping:**
  Quickly running commands or using REPLs to verify intuitive interfaces and expected behaviors remains invaluable.

* **Acceptance Testing and Stakeholder Validation:**
  Manual testing ensures clear understanding of acceptance criteria, confirming the system meets documented expectations before automation.

* **Complex UI or Auditory/Visual Checks:**
  Certain tests inherently require human perception, like verifying dynamic UI elements or auditory prompts.

Manual tests in these contexts prioritize learning, discovery, and interface clarity, crucial before locking in automated infrastructure.

---

## Automation First: Appropriate Use Cases

Automation-driven approaches—particularly leveraging AI or agents—are increasingly effective and efficient, especially in generating routine tests or purely mechanical coverage checks.

### Suitable Scenarios for Immediate Automation:

* **Coverage and Regression Tests:**
  Automatically generating tests to ensure broad code coverage and regression detection can be highly effective and efficient, skipping unnecessary manual repetition.

* **Bulk Test Migration and Scaffolding:**
  Using AI for rapid generation, scaffolding, and migration is invaluable. It accelerates large-scale test adoption without requiring manual pre-validation for every scenario.

* **Routine or Predictable Behavior Validation:**
  Automating simple, repetitive scenarios (like data exports or CLI outputs) from the start ensures consistent regression safety without manual overhead.

---

## Structured Acceptance Testing

The introduction of structured formats (e.g., `<gsl-acceptance-test>`) provides explicit clarity for tests, distinguishing clearly between performed actions, acceptance criteria, and expected results. This structured approach supports automated parsing, human readability, and precise test intent documentation:

```xml
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
```

Such explicit formats encourage clearer, actionable, and automatable tests.

---

## AI’s Role in Modern Testing

AI and automated agents have significantly altered testing practices by efficiently generating tests, scaffolding structures, and performing bulk migrations. Nevertheless, human judgment remains indispensable.

### AI Capabilities:

* **Efficient bulk test generation**
* **Automatic scaffolding and boilerplate reduction**
* **Rapid prototyping and migration**

### AI Limitations:

* **Cannot guarantee correctness or business intent**
* **Risk of false confidence if unchecked**

Thus, while AI accelerates test writing, human oversight ensures correctness, relevance, and meaningful intent.

---

## Recommended Hybrid Approach

A balanced testing strategy clearly distinguishes between acceptance tests (manual exploration valuable first) and coverage or regression tests (automation acceptable immediately).

### Recommended workflow:

1. **Acceptance and Exploratory Tests:**

   * Start manually for clarity, intuition, and interface validation.
   * Automate once stable and clearly defined.

2. **Coverage and Regression Tests:**

   * Leverage automated or AI-driven tests from inception.
   * Periodically validate automation-generated tests with manual checks to maintain confidence.

---

## Conclusion

Modern software development demands flexible, context-aware testing strategies. Recognize when manual exploration adds critical value, and when automation, aided by AI, can deliver faster, more efficient results. Embracing this hybrid approach ensures robustness, clarity, and sustained quality without unnecessary overhead.

---

*Happy testing—may your tests be insightful, efficient, and always aligned with your intent!*
