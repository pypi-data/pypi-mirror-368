# Acceptance Tests vs. Test Coverage

## 1. Introduction

In systems focused on declarative behavior and traceable correctness like OBK, the distinction between *test coverage* and *acceptance testing* is subtle yet critical. This article clarifies their differences and explains why both approaches are essential but fundamentally different.



## 2. Test Coverage Defined

**Test coverage** measures how much source code executes during testing.

#### ✅ What 100% Test Coverage Means:

* Every executable statement was executed at least once.
* Typically measured as *line coverage*.

#### ❌ What 100% Test Coverage Does Not Guarantee:

* Each statement has a dedicated test.
* All logic paths are tested.
* Behavior correctness.

#### 🧪 Types of Coverage:

* **Line Coverage**: Every line is executed.
* **Branch Coverage**: Each conditional branch (if/else, loops) is evaluated.
* **Path Coverage**: All possible execution paths through functions.
* **Condition Coverage**: All boolean conditions evaluated as true and false.



## 3. Practical Limitations of Test Coverage

#### 🔍 Limitations with SQL Queries

Coverage tools view complex SQL queries as simple statements:

```csharp
var sql = @"
    SELECT u.Id, u.Name
    FROM Users u
    LEFT JOIN Orders o ON o.UserId = u.Id
    WHERE o.Status = 'pending'
    ORDER BY o.CreatedAt DESC
";

var users = connection.Query<User>(sql);
```

* SQL logic is opaque to coverage tools.
* High coverage doesn't indicate correct SQL.

#### 🔍 Limitations with Chained Expressions (LINQ)

```csharp
var result = users
    .Where(u => u.IsActive)
    .Select(u => new { u.Id, u.Name })
    .OrderBy(u => u.Name)
    .ToList();
```

* Coverage granularity varies based on formatting.
* Terminal call (`.ToList()`) must be invoked to ensure execution.

**Best Practice:** Force query evaluation using `.ToList()`, `.Any()`, etc., to ensure the chain actually runs.



## 4. Automated Testing: Method vs. Motivation

Automation is a **method**, not a **motivation**. Tests can be automated for:

* Increasing code coverage.
* Verifying acceptance criteria.
* Routine sanity checks.

#### 🧭 Three Intersecting Axes:

| Axis          | Examples                          |
| ------------- | --------------------------------- |
| **Purpose**   | Coverage vs. Acceptance           |
| **Execution** | Automated vs. Manual              |
| **Scope**     | Unit vs. Integration vs. Workflow |

Automation does not inherently indicate purpose.



## 5. Acceptance Testing Defined

**Acceptance tests** validate whether the system meets stakeholder expectations and business rules.

#### ✅ Purposes of Acceptance Testing:

* Capture documented acceptance criteria.
* Ensure the system meets human-defined expectations.
* Provide assurance to stakeholders.



## 6. Acceptance Tests in Practice

#### 1. **Test That Cannot Be Automated**

**Example:** Confirm a voice-over accessibility prompt accurately reads dynamic UI content.

*Reason:* Requires human auditory perception.

#### 2. **Test You Would Not Want to Automate**

**Example:** System lockout after 10 failed login attempts, including audit verification.

*Reason:* High complexity, false positives, and cost.

#### 3. **Test You Do Automate (But Not for Coverage)**

**Example:** Exporting a CSV file correctly after multiple filters.

*Reason:* Clear scenario beneficial for continuous verification.


## 7. Structural Differences in Acceptance Tests

In OBK, acceptance tests follow a structured XML format, explicitly separating core testing aspects for clarity and ease of automation:

```xml
<gsl-acceptance-test>
  <gsl-acceptance-criteria>...</gsl-acceptance-criteria>  
  <gsl-performed-action>...</gsl-performed-action>
  <gsl-expected-result>...</gsl-expected-result>
</gsl-acceptance-test>
```

This clearly separates:

* **Acceptance Criteria**: The documented conditions, business rules, or requirements the system must satisfy for a test to be considered successful.
    
* **Action**: The specific steps or commands performed to execute the test.
    
* **Expectation**: The specific, observable outcome that proves the acceptance criteria were satisfied for this scenario.
    



#### Acceptance Criteria vs Expected Result

* #### **Acceptance Criteria**
    
    * **Definition:** The _predefined_ rule, requirement, or condition that must be satisfied for a feature or scenario to be considered acceptable to stakeholders or the business.
        
    * **Perspective:** Comes from _requirements/specification_ side (“what must be proven?”)
        
    * **Scope:** Usually high-level or rule-based; applies to a feature or behavior as a whole.
        
    * **Purpose:** _Why_ does this test exist? What rule or contract is it demonstrating?
        
    * **Example:**
        
        > “After 10 failed login attempts, the user must be locked out for 15 minutes.”
        
* #### **Expected Result**
    
    * **Definition:** The _concrete, observable outcome_ that should occur when the test scenario is executed.
        
    * **Perspective:** Comes from the _test_ side (“what should we see in this specific case?”)
        
    * **Scope:** Instance-level, often more specific than the criteria.
        
    * **Purpose:** _What_ specifically do we expect to see as evidence the criteria are met?
        
    * **Example:**
        
        > “After 10 incorrect passwords, the login form is disabled and a lockout timer is displayed to the user.”
        

#### The Benefits of Making Acceptance Criteria Optional but Expected Result Required

Allowing `<gsl-acceptance-criteria>` to be optional while requiring `<gsl-expected-result>` provides practical flexibility:

* **Avoids Unnecessary Repetition:**  
    Often, especially for internal or technical tests, the expected result fully describes what's needed. Writing separate criteria would duplicate information without added clarity.
    
* **Enables Faster Test Authoring:**  
    During rapid prototyping, exploratory tests, or migration, clear expected results can be captured without slowing down to formalize criteria.
    
* **Supports Both Formal and Informal Workflows:**  
    Formal stakeholder requirements benefit from explicit criteria for traceability. In informal contexts, meaningful tests can still be created without them.
    
* **Ensures Clear, Observable Evidence:**  
    Requiring an expected result ensures each test clearly documents the outcome proving correct behavior, making the tests effective for both human review and automation.
    
* **Reduces Boilerplate:**  
    Optional acceptance criteria prevent clutter in straightforward or routine test cases.
    

**In short:**  
This flexible structure ensures all acceptance tests clearly document what matters, without forcing unnecessary detail.




## 8. The Limits of AI in Acceptance Testing

AI can assist but cannot fully automate subjective test expectations.

#### ❌ AI Limitations:

* Cannot determine correctness or intent.
* Risk of false confidence from incorrect guesses.

#### ✅ AI Strengths:

* Scaffolding, outlining, and boilerplate.
* Idea generation and bulk migration.
* Structural validation and linting.

**Bottom Line:** AI accelerates tasks, but human judgment defines correctness.



## 9. Test Coverage vs Acceptance Testing: Quick Reference

| Purpose                          | Belongs in...      |
| -------------------------------- | ------------------ |
| Exercise every code path         | Test Coverage      |
| Verify user-facing outcomes      | Acceptance Testing |
| Ensure CLI prints correct info   | Acceptance Testing |
| Confirm all functions are called | Test Coverage      |
| Validate business rules          | Acceptance Testing |
| Detect dead code                 | Test Coverage      |



## 10. Human Judgment as the Core Differentiator

Coverage tools track execution, not correctness. Acceptance testing demands human-defined expectations, reflecting subjective intent and business context.



## 11. Conclusion

Testing strategies depend heavily on intent. Coverage provides execution safety, acceptance tests ensure behavioral correctness and trust.

Understanding this difference ensures effective and intentional testing, producing meaningful outcomes beyond mere metrics.
