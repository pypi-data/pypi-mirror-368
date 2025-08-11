# **Dogfooding OBK: Building for Self-Use**

* * *

## **What is OBK?**

OBK is a programmable system for documenting, validating, and querying project knowledge. It lets teams define prompts—describing inputs, outputs, workflows, and tests—in a structured, machine-readable way. Prompts are validated with XSD schemas, tracked in SQLite, and made available for both ad-hoc reporting and agent-driven queries. The ultimate goal is to connect OBK to agents that can answer detailed questions about a developing application using this structured data.

* * *

## **The Ambition: Self-Referential Systems**

A central principle in software is “dogfooding”: using your own tool to build or manage itself. For OBK, this means structuring OBK’s own design and development process using OBK prompts. Design discussions, migration notes, and test cases for OBK itself are captured, enabling real-time validation and feedback.

* * *

## **The Practicality: Bootstrapping and Incompleteness**

Developing a system like OBK while simultaneously trying to use it for its own development poses unique challenges:

* The schema and tooling are evolving as the system takes shape.
    
* Requirements may shift, meaning prompts and validation strategies will also change.
    
* The act of inventing and refining OBK is the primary focus at first, making full documentation in its own format a moving target.
    

This is not unique to OBK—any system that tries to fully describe or document itself will encounter practical bootstrapping limits. For OBK, this means there will always be aspects of its own development or operation that aren’t fully captured within the system.

* * *

## **The Vision: OBK in Use**

With OBK’s core features in place:

* OBK can describe, validate, and report on the structure and history of any project—including **some** of its own development.
    
* Prompts, acceptance tests, and process steps are all expressed and checked through the OBK framework.
    
* Agents can query OBK to retrieve detailed information about any OBK-managed application.
    
    

* * *

## **Summary**

Building a programmable prompt and documentation tool like OBK is an iterative process. Self-application isn’t a single milestone, but an ongoing demonstration of OBK’s capabilities as it evolves. As OBK develops, it increasingly uses its own features to describe and manage itself—showcasing its usefulness and flexibility in real-world, evolving projects.

* * *

_Dogfooding is not just a goal, but a marker of readiness. OBK is built with that destination in mind._

* * *
