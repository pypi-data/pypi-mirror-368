Development Roadmap
===================

This document outlines planned improvements for the pylint-sort-functions plugin based on real-world usage feedback.

Version 0.2.0 - Framework Awareness & Configuration
---------------------------------------------------

**Target**: Minor release with framework-specific handling

High Priority Features
~~~~~~~~~~~~~~~~~~~~~~

1. ✅ Framework-Aware Sorting (Completed)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: `#1 <https://github.com/hakonhagland/pylint-sort-functions/issues/1>`_ - Click decorators require functions to be defined before they can be referenced **(Closed)**

**Status**: ✅ **Implemented** - The ``ignore_decorators`` option is now available in both the PyLint plugin and auto-fix tool.

**Implementation**:

- ✅ Added ``ignore_decorators`` configuration option
- ✅ Parse decorator patterns and skip sorting requirements
- ✅ Support for any decorator pattern including Click, Flask, FastAPI, Celery

**Configuration Example**::

    # In CLI:
    pylint-sort-functions --ignore-decorators "@main.command" "@app.route"

    # In auto-fix config:
    config = AutoFixConfig(ignore_decorators=["@main.command", "@app.route"])

2. Enhanced Error Messages 📝
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: `#2 <https://github.com/hakonhagland/pylint-sort-functions/issues/2>`_ - Current messages don't show expected vs actual order

**Impact**: Medium - reduces developer productivity

**Complexity**: Low

**Current**::

    W9001: Functions are not sorted alphabetically in module scope

**Improved**::

    W9001: Functions are not sorted alphabetically in module scope
    Expected order: create, edit_config, main
    Current order: main, create, edit_config

3. pyproject.toml Configuration Support 🔧
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: `#3 <https://github.com/hakonhagland/pylint-sort-functions/issues/3>`_ - Modern Python projects prefer pyproject.toml over .pylintrc

**Impact**: Medium - affects adoption

**Complexity**: Low

**Configuration Example**::

    [tool.pylint.sort-functions]
    enable = ["unsorted-functions", "unsorted-methods"]
    ignore_decorators = ["@main.command"]
    test_method_ordering = "conventional"

Medium Priority Features
~~~~~~~~~~~~~~~~~~~~~~~~

4. Test Method Handling 🧪
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: `#5 <https://github.com/hakonhagland/pylint-sort-functions/issues/5>`_ - Test classes have conventional ordering (setUp, tearDown, test_*)

**Impact**: Medium - common use case

**Complexity**: Medium

**Configuration Options**:

- ``test_method_ordering = "conventional"`` - setUp/tearDown first, then alphabetical
- ``test_method_ordering = "alphabetical"`` - pure alphabetical sorting

5. Magic Methods Exclusion ✨
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: Magic methods (__init__, __str__) have conventional ordering

**Impact**: Medium - affects all classes

**Complexity**: Low

**Configuration**::

    [tool.pylint.sort-functions]
    ignore_magic_methods = true

6. Granular Disable Comments 🔇
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: Need fine-grained control over sorting requirements

**Impact**: Medium - developer convenience

**Complexity**: Medium

**Example**::

    class MyClass:
        def second_method(self):  # pylint: disable=unsorted-methods
            pass

        def first_method(self):
            pass

Version 0.2.1 - Auto-fix Improvements
--------------------------------------

**Target**: Patch release for auto-fix enhancements

1. Class Method Sorting in Auto-fix 🔧
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue**: Auto-fix tool currently only sorts module-level functions, not class methods

**Impact**: High - feature parity with PyLint plugin

**Complexity**: Medium

**Implementation**:

- Implement ``_sort_class_methods()`` in auto_fix.py
- Handle method extraction and sorting within classes
- Preserve class structure and indentation

Version 0.3.0 - Advanced Features
---------------------------------

**Target**: Minor release with auto-fixing and scope-specific rules

High Priority Features
~~~~~~~~~~~~~~~~~~~~~~

7. Batch Fix Utility 🛠️
^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: `#4 <https://github.com/hakonhagland/pylint-sort-functions/issues/4>`_ - Manually fixing many files is time-consuming

**Impact**: High - significant productivity improvement

**Complexity**: High

**Usage**::

    pylint-sort-fix src/ --dry-run   # Show what would change
    pylint-sort-fix src/ --apply     # Apply changes

**Features**:

- AST-based reordering preserving comments and formatting
- Backup creation before changes
- Integration with existing formatters (black, ruff)

8. Scope-Specific Configuration 🎯
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: Different scopes may need different sorting rules

**Impact**: Medium - flexibility for complex projects

**Complexity**: Medium

**Configuration**::

    [tool.pylint.sort-functions]
    module_functions = "alphabetical"
    class_methods = "alphabetical"
    test_classes = "conventional"

Medium Priority Features
~~~~~~~~~~~~~~~~~~~~~~~~

9. Auto-formatter Integration 📐
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: Ensure compatibility with black, ruff format, etc.

**Impact**: Medium - prevents formatting conflicts

**Complexity**: Medium

**Features**:

- Preserve existing formatting during reordering
- Test compatibility with major formatters
- Document recommended usage order

10. Edge Case Investigation 🔍
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue**: False positives in complex scenarios

**Impact**: Medium - reduces false positives

**Complexity**: High

**Areas to Investigate**:

- Mixed class/function detection
- Comment-separated function groups
- Conditional imports affecting order
- Nested function handling

Version 0.4.0 - Polish & Stability
----------------------------------

**Target**: Minor release focusing on stability and edge cases

- Address remaining edge cases and false positives
- Performance optimizations for large codebases
- Comprehensive documentation and examples
- Plugin ecosystem integration (pre-commit, VS Code, etc.)

Implementation Strategy
-----------------------

Phase 1: Quick Wins (0.2.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Focus on configuration and user experience improvements that don't require major architectural changes:

1. Enhanced error messages (1-2 days)
2. pyproject.toml support (2-3 days)
3. Magic methods exclusion (1 day)
4. Framework decorator ignoring (3-4 days)

**Estimated Timeline**: 2-3 months

Phase 2: Advanced Features (0.3.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tackle more complex features requiring significant development:

1. Test method handling (1 week)
2. Scope-specific configuration (1 week)
3. Batch fix utility (2-3 weeks)
4. Auto-formatter integration (1 week)

**Estimated Timeline**: 4-6 months

Phase 3: Polish & Edge Cases (0.4.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Address remaining edge cases and polish:

1. Granular disable comments (1 week)
2. Edge case investigation and fixes (2-3 weeks)
3. Comprehensive documentation and examples (1 week)

**Estimated Timeline**: 6-8 months

Success Metrics
---------------

- **Adoption**: Reduce false positives by >80%
- **Usability**: Enable auto-fixing for >90% of violations
- **Framework Support**: Support top 5 Python web frameworks
- **Developer Experience**: Reduce manual fixing time by >70%

Contributing
------------

Each improvement should include:

- ☐ Implementation with tests
- ☐ Documentation updates
- ☐ Configuration examples
- ☐ Migration guide (if breaking changes)
- ☐ Performance impact assessment

Getting Involved
----------------

- **Report Issues**: Share your use cases and edge cases on `GitHub <https://github.com/hakonhagland/pylint-sort-functions/issues>`_
- **Feature Requests**: Describe your specific needs and constraints
- **Code Contributions**: Pick up any issue labeled "good first issue"
- **Testing**: Try pre-release versions on your projects

.. note::
   This roadmap is based on real-world usage feedback and will be updated as priorities evolve.
   Timeline estimates are approximate and depend on contributor availability.
