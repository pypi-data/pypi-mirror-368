# Task: Organize and Rename Python Tests by Type

## Context:

We have an existing test suite in the top-level directory `tests/`. We now want to reorganize it into three clear categories based on test types:

* **Unit tests**
    
* **Integration tests**
    
* **Acceptance tests**
    

## Definitions and Detection Criteria:

Use the following clear criteria to detect test type:

### **1. Unit Tests (Highest Precedence)**

* Tests exactly **one module, class, or function**.
    
* No interaction with external services (e.g., APIs, databases, filesystem).
    
* Often imports only the module under test and standard libraries or mocks.
    
* Should be placed in `tests/unit/` and **renamed to exactly match** the tested module:
    
    * For `validation.py`, the unit test is `tests/unit/test_validation.py`.
        

### **2. Integration Tests (Medium Precedence)**

* Tests interactions between **multiple modules or services**.
    
* Might involve external resources (filesystem, database, network).
    
* Usually includes tests of APIs, databases, CLI, or filesystem interactions.
    
* Should be placed in `tests/integration/`.
    
* Naming convention should clearly describe integration:
    
    * E.g., `test_cli_integration.py`, `test_db_and_api.py`.
        

### **3. Acceptance Tests (Lowest Precedence)**

* Tests end-to-end user flows, business scenarios, or acceptance criteria.
    
* Typically involves multiple layers of the app or full-stack simulation.
    
* Should be placed in `tests/acceptance/`.
    
* Naming convention clearly describes the business case:
    
    * E.g., `test_user_login_acceptance.py`, `test_prompt_end_to_end.py`.
        

## Precedence in Case of Ambiguity:

If a test fits multiple categories, always choose the **higher precedence category**:

* **Unit** > **Integration** > **Acceptance**
    

## Task Instructions:

1. **Analyze existing test files in `tests/`**.
    
2. Determine clearly:
    
    * Is it a unit, integration, or acceptance test? (Use the definitions above.)
        
    * If unsure or overlapping, pick the higher-priority category (unit first, then integration, then acceptance).
        
3. **Organize files by type**:
    
    * Move to the correct folder: `tests/unit/`, `tests/integration/`, or `tests/acceptance/`.
        
4. **Rename unit test files**:
    
    * Each unit test file **must exactly mirror** the name of the module it tests.
        
    * Example: if a file tests `validation.py`, rename it to `test_validation.py`.
        
    * Do **not** rename integration or acceptance tests unless absolutely needed for clarity.
        
5. **Do not** refactor test code, add new tests, remove existing tests, or modify test contents beyond file relocation and unit test renaming.
    
6. Ensure all test files begin with `test_` so pytest auto-discovers them.
    

## Example Final Directory Structure:

```
tests/
  unit/
    test_validation.py          # tests validation.py
    test_services.py            # tests services.py
    ...
  integration/
    test_cli_integration.py
    test_db_and_api.py
    ...
  acceptance/
    test_user_login_acceptance.py
    test_prompt_end_to_end.py
    ...
  fixtures/
    ...
  conftest.py
```

**End of Task**

* * *
