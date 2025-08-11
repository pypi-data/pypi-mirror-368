# Chem++

**Chem++** is a domain-specific programming language and runtime for computational chemistry,
integrating a C++-like syntax with chemistry-specific types and functions and optional
PubChem lookup support. This package provides:

- A fully functional interpreter (`chempp.interpreter`) for the Chem++ language.
- A Safe API wrapper (`chempp.safe_api`) that enforces Parse → Analyze → Interpret order,
  provides PubChem caching + fallback, and exposes synchronous and asynchronous run helpers.
- A chemistry registry with common types (Atom, Molecule, Reaction) and helper functions.
- Toolkit features for Jupyter notebook integration, static analysis hooks, and a small cache.

## Quickstart

```python
import chempp.safe_api as cs

code = '''
float main() {
    // example: create a molecule object and fetch basic property
    Molecule water("H2O");
    float w = molecular_weight("H2O");
    return 0;
}
'''
# synchronous run
result = cs.run(code)

# asynchronous run (useful in notebooks)
import asyncio
asyncio.run(cs.run_async(code))
