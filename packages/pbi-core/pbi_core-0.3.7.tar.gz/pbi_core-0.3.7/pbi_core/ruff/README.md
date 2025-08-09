✅ DAX Linting Rules
Style & Readability
Indentation & Formatting
Enforce consistent indentation (e.g., 2 or 4 spaces) and line breaks for readability.

Keyword Casing
Ensure DAX keywords (CALCULATE, FILTER, etc.) are uppercase.

Avoid SELECTCOLUMNS abuse
Flag overuse or misuse where better alternatives like ADDCOLUMNS or SUMMARIZE would be more performant.

Explicit measure references
Suggest always using [MeasureName] instead of ambiguous column references.

Performance
Avoid use of EARLIER in deeply nested contexts
It's error-prone and slow—recommend VAR + FILTER pattern instead.

Avoid CALCULATE inside FILTER unless necessary
Often indicates overly complex or redundant expressions.

Detect unnecessary ALL or REMOVEFILTERS
Warn when context removal is used but not needed.

Flag use of FILTER(ALL(...)) instead of ALLSELECTED or proper KPI-friendly logic
Helps avoid misleading metrics.

Warn for row context in measures
E.g., using RELATED or EARLIER inside a measure when it doesn’t make sense.

Best Practices
Suggest use of VAR for reused expressions
Improves readability and performance.

Flag magic numbers
Encourage defining constants via parameters or variables.

Use DIVIDE instead of /
Handles division-by-zero safely.

Avoid hardcoded column names inside strings
Breaks easily with schema changes.

✅ Layout Linting Rules (from Report/Layout JSON)
Consistency
Font size standardization
Warn if text visuals use inconsistent font sizes across pages.

Color palette enforcement
Check against a predefined theme or brand color palette.

Label truncation
Flag visuals where axis or title labels are cut off or ellipsed.

Inconsistent alignment
Check if visuals are slightly misaligned (e.g., 1–2 px off).

Overlapping visuals
Detect when visuals physically overlap in layout.

Accessibility
Low contrast text
Warn if font/background combinations fail accessibility contrast standards.

Missing titles or descriptions
Flag visuals that don’t have accessible names or tooltips.

Tab order inconsistencies
Ensure keyboard/tab navigation order is logical.

Structural
Duplicate visuals
Detect identical visuals (same filters/metrics) used repeatedly.

Unused bookmarks or selections
Flag bookmarks, slicer states, or drillthrough pages that are defined but never used.

🧠 More DAX Linting Rules
Maintainability
Overly complex expressions
Warn when a measure or column exceeds a threshold of lines or nested functions.

Deeply nested IF statements
Recommend SWITCH for clarity and maintainability.

Redundant variables
Detect declared VARs that are never used or repeated unnecessarily.

Circular logic risk
Flag patterns that may create dependencies across calculated columns/measures (e.g., bidirectional filter + calculated column using related measure).

Inconsistent naming conventions
E.g., [TotalSales] vs. [SalesTotal]—recommend rules like PascalCase, noun-first, verb-later, etc.

Data Modeling Pitfalls
Measures referencing calculated columns unnecessarily
Suggest calculating directly from base columns when feasible.

Use of calculated columns instead of measures
Warn when a column logic could be expressed more efficiently as a measure.

Time intelligence misuse
Detect when time functions (e.g., SAMEPERIODLASTYEAR) are used without a proper date table marked.

Too many distinct measures in a single table
Recommend separating measures into dedicated “Measure Tables” for organization.

Measures referencing inactive relationships without USERELATIONSHIP
Warn for likely bugs or confusion.

🎨 More Layout Linting Rules
Design Consistency
Non-standard page sizes
Warn if report pages deviate from standard sizes (16:9, Letter, etc.).

Misaligned slicers
Detect inconsistent slicer placement or orientation across pages.

Inconsistent visual types for same metrics
E.g., using a bar chart on one page and a card on another for the same measure.

Unused visuals (blank or static)
Flag visuals with no data bound or visuals showing constant/static values.

Missing report/page headers
Recommend consistent header bars or titles for navigation and UX.

UX Optimization
Too many visuals per page
Warn when a page is overloaded (>N visuals), which hurts usability and performance.

Lack of filters or slicers on dense pages
Recommend adding at least basic interactivity/filtering when many visuals exist.

No indication of drillthrough availability
Suggest marking or guiding users to drillthrough features.

Governance & Performance
Hidden visuals or pages still present
Warn if hidden visuals/pages exist but are still loaded—may confuse users or waste resources.

Static KPIs or hardcoded numbers in textboxes
Flag if key metrics are manually typed rather than bound to measures.

Large embedded images or media files
Warn if assets exceed a size threshold (impacts report load times).

Deprecated visuals used
Detect use of outdated custom visuals or visuals deprecated by Microsoft.

🔧 Tooling Enhancements (for your linter)
Rule severity levels (info, warn, error)

Auto-fix suggestions for simple issues (e.g., keyword casing, naming)

Rule tagging (performance, style, governance) for filtering

Configurable thresholds (e.g., "no more than 10 visuals per page")

🧾 Power Query M Linting Rules
📐 Style & Readability
Consistent Indentation and Spacing
Enforce 2/4-space indentation, consistent use of line breaks and spacing around operators (=, =>, +, etc.).

Keyword Casing
Standardize casing for M functions (let, in, each, if, then, else, etc.). Prefer lowercase or configurable.

Explicit Step Naming
Flag generic or meaningless step names like #"Changed Type1", #"Renamed Columns2"—suggest descriptive names.

Avoid Overly Long Step Chains
Warn if too many chained steps exist without intermediate let bindings—harms readability and debugging.

Unused Steps
Detect when a step is defined but never referenced in the final output.

Duplicate Step Names
M allows multiple steps named similarly with number suffixes—warn for clarity issues.

🚦 Performance Optimization
Avoid Auto-Type Detection
Flag reliance on Table.PromoteHeaders or Changed Type without explicit types—leads to implicit coercion and slow queries.

Push Filters Early
Suggest moving Table.SelectRows or filtering steps as early as possible in the query for query folding and performance.

Detect Non-Foldable Steps
Identify known steps that break query folding (e.g., Table.Buffer, List.Generate, Table.Sort in wrong context).

Avoid Table.Buffer Unless Justified
Warn about memory-heavy buffering unless explicitly needed for non-folding or caching.

Warn on Custom Column Loops
Flag performance issues from Table.AddColumn with List operations or nested each that don’t fold.

🛡️ Governance & Safety
Hardcoded Credentials or Secrets
Flag any step with embedded usernames, passwords, or API tokens in URL/query strings.

Hardcoded File Paths or URLs
Warn when fixed local paths or environments are used—encourage use of parameters.

External Data Sources Without Parameters
Suggest parameterizing all external references for portability (e.g., file path, server name).

Disable Load but Used
Warn when a query is marked as “disable load” but referenced by others—may cause confusion.

📊 Modeling & Query Design
Use of Merge Without Join Kind
Merges without explicit join kind (JoinKind.Inner, etc.) default to LeftOuter—make it explicit for clarity.

Missing Column Type Definitions
Enforce explicit column typing after transformations like merges, pivots, and column additions.

List functions returning inconsistent types
Warn when List.Transform, List.Select, etc. return types not matching the expected schema.

Unused Parameters
Flag report or query parameters defined but unused anywhere in the query logic.

Pivot/Unpivot without Null Handling
Suggest using Table.FillDown, ReplaceValue, or similar when pivoting/unpivoting introduces nulls.

📦 Deployment-Ready Practices
Queries Named “Query1”, “Query2”, etc.
Flag default-named queries and suggest renaming for clarity and traceability.

Nested Queries vs Function Reuse
Recommend factoring out logic into shared functions when repeating logic across queries.

Excessive Column Renaming Steps
Warn when multiple Table.RenameColumns steps are chained—suggest consolidation.

Locale-sensitive operations
Flag functions like DateTime.FromText without locale—behavior may differ across environments.

Binary columns in tables
Warn if binary data (e.g., files, images) is unnecessarily loaded into the model.

🔧 Suggested Tool Features
Configurable rule thresholds (e.g., max steps per query, max step name length)

Fix suggestions or auto-fixes for style rules (indentation, casing)

Rule tagging (e.g., performance, readability, safety)

Severity levels: info, warning, error

Plugin system to support custom enterprise rules