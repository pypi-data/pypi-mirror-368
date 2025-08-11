Group of rules related to DAX formatting.



# DAX-001: Camel Case Variable Names

**Applies to:**

- [Measure](/SSAS/entities/measure)

**Fix State:** Not Automatically Fixable

```

Variable names in DAX expressions should be in camelCase format.
This helps maintain consistency and readability in DAX expressions.

```

# DAX-002: Camel Case Measure Names

**Applies to:**

- [Measure](/SSAS/entities/measure)

**Fix State:** Not Automatically Fixable

```

Measure names in DAX expressions should be in camelCase format.
This helps maintain consistency and readability in DAX expressions.

```

# DAX-003: Unused Measure Variables

**Applies to:**

- [Measure](/SSAS/entities/measure)

**Fix State:** Not Automatically Fixable

```

Measures should not contain unused variables.
This helps maintain clarity and (in some cases?) performance in DAX expressions.

```

# DAX-004: Magic Numbers in DAX Expressions

**Applies to:**

- [Measure](/SSAS/entities/measure)

**Fix State:** Not Automatically Fixable

```

DAX expressions should not contain magic numbers.
Magic numbers are numeric literals that appear in the code without explanation.
They can make the code harder to understand and maintain.
If the number is used multiple times, it should be assigned to a measure. If it is used only once,
it should be assigned to a variable with a descriptive name.

Basic numbers: (1, 2, 3, 7, 30, 100, 1000) are excluded from this rule.

```

# DAX-007: Capitalize Function Names

**Applies to:**

- [Measure](/SSAS/entities/measure)

**Fix State:** Not Automatically Fixable

```

Function names in DAX expressions should be upper case.
This helps maintain consistency and readability in DAX expressions.

```
