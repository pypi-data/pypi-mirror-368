# Why One-Line Manual Tests Should Precede Automation


_— And when you think about it, it's impossible not to._

---

#### Counter Dogma With Anti-Dogma

Let’s call it what it is: it’s a logical impossibility to automate a test you haven’t first performed—manually, in your head, in your shell, or on paper. Anyone who claims otherwise is either redefining "test" to mean "mechanical assertion,” or ignoring the real, messy, human work of discovery.

Test-Driven Development (TDD) is widely regarded as one of the most effective ways to build robust software. But somewhere along the way, the conversation shifted from **"write the test first”** to **"automate everything from day one.”** In reality, the original spirit of TDD—and the pragmatic workflow of high-performing developers—starts with simple, manual, one-line tests.

If you’ve ever found yourself hesitating to write a test because of the "ceremony” involved, this article is for you.

---

#### Manual, One-Line Tests: The Real First Step


Let’s break down what happens when you’re prototyping a new feature or CLI tool. What do you do first?  
You _don’t_ usually open a test file and start importing pytest.  
Instead, you:

* Run a command in your shell:
    
    ```sh
    obk hello --name Ada
    ```
    
* Or try something in a Python REPL:
    
    ```python
    >>> add(2, 3)
    5
    ```
    

That’s a **test**. In the purest sense, you’re specifying desired behavior and observing what happens. This is _manual TDD_, and it’s not only valid—it’s efficient.

---

#### Why Manual Tests First?


##### 1. Clarity and Feedback Before Infrastructure

Writing a manual one-liner forces you to focus on _what_ you want, not _how_ to automate it. You get immediate, visual feedback—was the output right? Did it crash? Is this the right interface?  
You’re learning, not yet committing to infrastructure.

##### 2. Discovering What Actually Matters

Premature automation is a form of waste. If you don’t know the right behavior or interface yet, why lock it into a test suite? Manual tests let you rapidly experiment and change your mind, discovering edge cases and pain points in real time.

##### 3. Automation is an Optimization, Not the Point

Automation is powerful because it makes feedback fast and repeatable. But it’s an optimization. The real heart of TDD is _learning_—proving that your code meets your intent.  
Once your manual test proves valuable (and you like the interface), **then** you automate it for regression safety and efficiency.

##### 4. Transitioning is Trivial

If you keep your manual tests concise, transitioning them to automation is easy. That CLI line becomes a test case in pytest or a shell script. Your shell history, scratch files, or README become a living record of user expectations.

---

#### Program to an Interface, Not an Implementation
<sup>— Inspired by the *Design Patterns* “Gang of Four” (Gamma, Helm, Johnson, Vlissides)</sup>

One advantage of starting with manual, one-line tests is that you’re naturally thinking in terms of **interfaces**—the commands, functions, or behaviors you want to interact with. You’re not tied to a specific implementation; you’re specifying _what_ you expect, not _how_ it’s done.

This mindset, famously encapsulated as **“program to an interface, not an implementation,”** is foundational to good design. By testing the interface you want—before you automate or even write the real code—you give yourself the freedom to refactor, optimize, or swap out implementations later, with minimal friction.

Manual testing encourages you to keep interfaces simple, composable, and intuitive—because you’re using them _yourself_, in real time.  
Later, when you automate, your tests are more robust and future-proof because they’re anchored to clear, well-thought-out interfaces, not accidental details.

---

#### A Historical Note: TDD Originators Didn’t Require Automation


The pioneers of TDD—Kent Beck, the Extreme Programming crowd—cared about "test first,” not "automate first.” A test could be a script, a REPL snippet, or even a written checklist. Automation became the norm because it’s repeatable and fast, but it isn’t the definition of TDD.  
**You are practicing TDD any time you specify the desired behavior before writing code—no matter how you express it.**

---

#### A Pragmatic Workflow: Manual One-Liners → Automated Tests


1. **Write a single-line manual test:**
    
    * Shell: `obk hello --name Ada`
        
    * REPL: `add(2, 3)`
        
2. **Observe and learn:**
    
    * Did it work?
        
    * Was the output correct?
        
    * Is this the right interface?
        
3. **Refine your code and your "test” until you’re happy.**
    
4. **Promote it to automation:**
    
    * Pytest:
        
        ```python
        def test_hello():
            assert CliRunner().invoke(cli, ['hello', '--name', 'Ada']).output == "Hello, Ada!\n"
        ```
        
    * Shell script:
        
        ```sh
        [ "$(obk hello --name Ada)" = "Hello, Ada!" ]
        ```
        

---

#### Best Practices


* **Document your manual tests:** Keep a running list in your README, docs, or a scratch file. This helps you (and your team) remember what "working” looks like.
    
* **Automate once stable:** As soon as you know the test is valuable and the behavior/interface is stable, automate it for regression safety.
    
* **Don’t fear manual steps:** They’re the root of all effective automation. Good test suites are made from many "manual experiments” that proved their worth—you cannot automate something that you do not know how to do manually.
    

---

**Conclusion**
--------------

Manual, one-line tests aren’t just an acceptable precursor to automation—they’re the _smartest_ way to do TDD in the real world. They foster learning, reduce wasted effort, and lead to cleaner, more effective test suites.  
Don’t let dogma about "automation first” get in your way. **Prove value manually, then automate. That’s true TDD.**

---

_Happy hacking—and may your one-liners always teach you something valuable before you automate them!_