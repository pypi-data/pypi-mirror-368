# AGENTS.md

---

## GSL Prompt Files

#### 1. Overview

This section describes the schema, structure, and business rules for OBK GSL Prompt Markdown files containing customer XML. They are used to define agent prompts in the OBK system.

- All prompt files **must** validate against the authoritative XML Schema (`prompt.xsd`).
- Additional business rules (e.g., ID uniqueness) are enforced by downstream tooling or the database layer.



#### 2. Element Reference

##### 2.1 Root Element – `<gsl-prompt>`

*Attributes*  
- **id** (required): Unique trace ID (`traceIdType`, `YYYYMMDDTHHmmSS±ZZZZ`).  
- **type** (required): One of `feat | fix | build | chore | ci | docs | style | refactor | perf | test`.  
- **changelog** (optional): `"true"` or `"false"` (**must be lowercase**).

*Children (in order)*  
1. `<gsl-label>` (optional)  
2. `<gsl-title>` (optional)  
3. `<gsl-description>` (optional)  
4. `<gsl-value>` (optional)  
5. `<gsl-header>` (**required**)  
6. `<gsl-block>` (**required**)


> Only the elements and attributes described here are valid within the `<gsl-prompt>` XML element and its children. Elements or attributes not defined in the schema (such as `<div>`) will cause XML schema validation to fail.

##### 2.2 Global Fields (may appear in many containers)

- `<gsl-label>` – Text label  
- `<gsl-title>` – Title or summary  
- `<gsl-description>` – Detailed description  
- `<gsl-value>` – Arbitrary value or data  

##### 2.3 <gsl-header>

- **Required.** Must appear **exactly once** as a direct child of `<gsl-prompt>`, after any global fields and before `<gsl-block>`.
- **Content:** A single text value (no child elements, no attributes).
- **Purpose:** Used as the canonical, displayable header for the agent prompt.



##### 2.4 Main Block Structure – `<gsl-block>`

Children **must appear in this order**; for elements marked *required*, they must appear **exactly once**. For all others, at most once (if present).

1. `<gsl-label>` (optional, at most once)
2. `<gsl-title>` (optional, at most once)
3. `<gsl-description>` (optional, at most once)
4. `<gsl-value>` (optional, at most once)
5. `<gsl-purpose>` (**required**, exactly once)
6. `<gsl-inputs>` (**required**, exactly once)
7. `<gsl-outputs>` (**required**, exactly once)
8. `<gsl-workflows>` (**required**, exactly once)
9. `<gsl-acceptance-tests>` (**required**, exactly once)
10. `<gsl-breaking-change>` (optional, at most once)


> *Note:* Optional elements may appear at most once. Required elements must appear exactly once.
The global fields (label, title, description, value) must always be in this order.



##### 2.5 Acceptance Test Branch

###### 2.5.1 `<gsl-acceptance-tests>`

- Must contain **one or more** `<gsl-acceptance-test>` elements.
- May contain, in this order and at most once each:  
    1. `<gsl-label>` (optional)  
    2. `<gsl-title>` (optional)  
    3. `<gsl-description>` (optional)  
    4. `<gsl-value>` (optional)
- These fields, if present, must appear before any `<gsl-acceptance-test>`.


###### 2.5.2 `<gsl-acceptance-test>`

*Attributes*  
- **id** (required): Unique trace ID matching the pattern `YYYYMMDDTHHmmSS±ZZZZ` (specifically: eight digits for date, a 'T', six digits for time, a plus or minus, then four digits for the time zone offset; e.g., `20250805T153000+0000`).  
    **Pattern:** `\d{8}T\d{6}[+-]\d{4}`
- **manual-only** (optional): `"true"` or `"false"` (**must be lowercase**).

*Children (in order; first four are Global Fields and may each appear at most once):*

1. `<gsl-label>` (optional)
2. `<gsl-title>` (optional)
3. `<gsl-description>` (optional)
4. `<gsl-value>` (optional)
5. `<gsl-filename>` (optional, 0‥1)
6. `<gsl-user-type>` (optional, 0‥1)
7. `<gsl-acceptance-criteria>` (optional, 0‥1)
8. `<gsl-performed-action>` (**required**, exactly 1)
9. `<gsl-expected-result>` (**required**, exactly 1)

> *Note:* The first four elements must appear in this exact order (if present), and at most once each.



#### 2.6 Breaking Change Section – `<gsl-breaking-change>` (optional, at most once)

- If present, `<gsl-breaking-change>` must appear in this order:
    1. `<gsl-label>` (optional, at most once)
    2. `<gsl-title>` (optional, at most once)
    3. `<gsl-description>` (optional, at most once)
    4. `<gsl-value>` (optional, at most once)
    5. `<gsl-language-maintenance>` (required, exactly once)  
        - Content: text only (no child elements, no attributes)
    6. `<gsl-content-migration>` (required, exactly once)  
        - Content: text only (no child elements, no attributes)





#### 2.7 Other Single‑Purpose Containers

Each of the following elements:
- `<gsl-purpose>`
- `<gsl-inputs>`
- `<gsl-outputs>`
- `<gsl-workflows>`


**May contain, in this order (all optional, at most once each):**
1. `<gsl-label>`
2. `<gsl-title>`
3. `<gsl-description>`
4. `<gsl-value>`

No other elements are permitted inside these containers.




#### 3. Validation & Business Rules

##### 3.1 XSD‑Enforced Rules

3.1.1 Element order, cardinality, and text/Non‑Text constraints follow the sequences above.  
3.1.2 `<gsl‑prompt>` `type` attribute **must** be one of the ten enumerated values.  
3.1.3 Boolean attributes (`changelog`, `manual-only`) accept only `"true"` or `"false"` (**must be lowercase**).

##### 3.2 Business / Implementation Rules

3.2.1 **Trace ID uniqueness:** `id` on `<gsl‑prompt>` must be unique across all prompt files.  
3.2.2 **Acceptance test ID uniqueness:** `id` on `<gsl‑acceptance-test>` must be unique within a file.  
3.2.3 If `<gsl-breaking-change>` is present, both `<gsl-language-maintenance>` and `<gsl-content-migration>` must appear exactly once, in that order.  
3.2.4 Each file contains exactly **one** `<gsl-prompt>` root element.

##### 3.3 Custom / Project‑Specific Rules

3.3.1 _Add additional organization‑specific rules here as they are adopted._



#### 4. Change History

*(Record significant schema or policy changes with dates.)*



#### 5. Example – Minimal Valid Prompt

```xml
<gsl-prompt id="20250805T120000+0000" type="feat">
  <gsl-label>Example Agent</gsl-label>
  <gsl-header>Sample Header</gsl-header>

  <gsl-block>
    <gsl-purpose>
      <gsl-title>Purpose</gsl-title>
      <gsl-description>Explain what the agent does.</gsl-description>
    </gsl-purpose>

    <gsl-inputs>
      <gsl-label>Input Files</gsl-label>
      <gsl-value>config.yml</gsl-value>
    </gsl-inputs>

    <gsl-outputs>
      <gsl-label>Outputs</gsl-label>
      <gsl-value>analysis.json</gsl-value>
    </gsl-outputs>

    <gsl-workflows>
      <gsl-title>Steps</gsl-title>
      <gsl-description>Step‑by‑step guide …</gsl-description>
    </gsl-workflows>

    <gsl-acceptance-tests>
      <gsl-acceptance-test id="T1">
        <gsl-title>Happy‑path login</gsl-title>
        <gsl-user-type>admin</gsl-user-type>
        <gsl-performed-action>Log in with valid credentials</gsl-performed-action>
        <gsl-expected-result>Dashboard is displayed</gsl-expected-result>
      </gsl-acceptance-test>
    </gsl-acceptance-tests>

    <!-- Optional breaking change -->
    <!--
    <gsl-breaking-change>
      <gsl-language-maintenance>Update deprecated API calls.</gsl-language-maintenance>
      <gsl-content-migration>Transform existing JSON files.</gsl-content-migration>
    </gsl-breaking-change>
    -->
  </gsl-block>
</gsl-prompt>
```
---