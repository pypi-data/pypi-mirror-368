## Task: Achieve 100% Test Coverage for Python Codebase

**Goal:**  
Continuously run `pytest -q --cov` and make targeted changes to Python test files under the `tests/` folder until test coverage is **100%**.

**Instructions:**

1. **Run Coverage:**
    
    * Run `pytest -q --cov` to collect the current coverage report.
        
2. **Analyze Gaps:**
    
    * Identify all uncovered lines, branches, or files.
        
3. **Update or Add Tests:**
    
    * Un-comment, update, or refactor existing commented-out tests in the `tests/` folder if they help achieve coverage.
        
    * If commented-out tests are obsolete or do not help coverage, consider deleting them.
        
    * Create new tests as needed to cover the remaining uncovered code.
        
4. **Repeat:**
    
    * Re-run `pytest -q --cov` after each change or set of changes.
        
    * Continue making incremental improvements until **100% coverage** is reported.
        
5. **Code Quality:**
    
    * Ensure all new or modified tests are clean, readable, and follow project conventions.
        
    * Only delete commented-out tests if you are certain they do not contribute to meaningful coverage.
        
6. **Exit Criteria:**
    
    * The task is complete when `pytest -q --cov` reports **100% coverage** across all relevant files.
        

* * *

**Notes:**

* Only modify files in the `tests/` directory.
    
* Do not alter non-test code except as absolutely necessary to enable testing (e.g., making code importable).
    
* Log or summarize each set of changes (which tests were uncommented, deleted, or added).
    
* If 100% coverage cannot be achieved (e.g., due to unreachable code), document any exceptions and halt.
    

* * *