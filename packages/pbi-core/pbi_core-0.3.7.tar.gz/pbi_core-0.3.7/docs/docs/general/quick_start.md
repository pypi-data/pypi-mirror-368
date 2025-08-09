## Basic Functionality

This basic example tests that your PowerBI report can be parsed and reassembled by ``pbi_core``. 


```python3

from pbi_core import LocalReport

report = LocalReport.load_pbix("example.pbix")  # (1)!
report.save_pbix("example_out.pbix")  # (1)!
```

1. hi

## Altering Data model

This example shows how you can add automatic descriptions to PowerBI columns (possibly from some governance tool??)


```python3

from pbi_core import LocalReport

report = LocalReport.load_pbix("example.pbix")
for column in report.ssas.columns:
    column.description = "pbi_core has touched this"
    column.alter()  # saves the changes to the SSAS DB

report.save_pbix("example_out.pbix")
```

Finding records in SSAS tables
------------------------------

This example shows how to find SSAS records and extract data from report columns

```python3
from pbi_core import LocalReport

report = LocalReport.load_pbix("example.pbix")
values = report.ssas.columns.find({"explicit_name": "a"}).data()
print(values)
values2 = report.ssas.tables.find({"name": "Table"}).data()
print(values2)

measure = report.ssas.measures.find({"name": "Measure"})
column = measure.table().columns()[1]  
# Note: the first column is a hidden row-count column that can't be used in measures
values3 = measure.data(column, head=10)
print(values3)
```

## pbi_core Lineage Chart

This example displays a lineage chart in HTML:

```python3
from pbi_core import LocalReport

report = LocalReport.load_pbix("example.pbix", kill_ssas_on_exit=True)
col = report.ssas.columns.find({"explicit_name": "MeasureColumn"})
col.get_lineage("parents").to_mermaid().show()
```

## Improved Multilanguage Support

This example displays the ability to easily convert PBIX reports to alternate languages:

```python
from pbi_core import LocalReport
from pbi_core.misc.internationalization import get_static_elements, set_static_elements

report = LocalReport.load_pbix("example.pbix", kill_ssas_on_exit=True)
x = get_static_elements(report.static_files.layout)
x.to_excel("multilang.xlsx")

set_static_elements("multilang1.xlsx", "example.pbix")
```

## Automatic Data Model Cleaning

One of the core tensions in PowerBI is the size of the data model. In development, you want to have many measures, columns, and tables to simplify new visual creation. After developing the report, the additional elements create two issues:

1. It's difficult to understand which elements are being used and how they relate to each other
2. The additional columns and tables can slow down visual rendering times, negatively impacting UX

pbi_core has an automatic element culler that allows you to remove unnecessary elements after the report has been designed:

```python

from pbi_core import LocalReport

report = LocalReport.load_pbix("example_pbis/api.pbix")
report.cleanse_ssas_model()
report.save_pbix("cull_out.pbix")
```

## Performance Analysis

This example shows how to analyze the performance of a Power BI report's visual:

!!! warning

    In the current implementation, the performance trace occassionally hangs. If this happens, you can kill the process and restart it. This is a known issue that will be fixed in a future release.


```python

from pbi_core import LocalReport

report = LocalReport.load_pbix("example_pbis/example_section_visibility.pbix")
# x = report.static_files.layout.sections[0].visualContainers[0].get_performance(report.ssas)
x = report.static_files.layout.sections[0].get_performance(report.ssas)
print(x)
print("=================")
print(x[0].pprint())
```

Which generates the following output.

```shell
2025-07-05 14:07:31 [info     ] Loading PBIX                   path=example_pbis/example_section_visibility.pbix
2025-07-05 14:07:33 [warning  ] Removing old version of PBIX data model for new version db_name=example_section_visibility
2025-07-05 14:07:33 [info     ] Tabular Model load complete   
2025-07-05 14:07:35 [info     ] Beginning trace               
2025-07-05 14:07:38 [info     ] Running DAX commands          
2025-07-05 14:07:41 [info     ] Terminating trace             
[Performance(rows=5, total_duration=0.0, total_cpu_time=0.0, peak_consumption=1.0 MiB]
=================
Performance(
    Command:

        DEFINE VAR __DS0Core =
                SUMMARIZECOLUMNS('example'[b], "Suma", CALCULATE(SUM('example'[a])))

        EVALUATE
                __DS0Core

    Start Time: 2025-07-05T19:07:38.450000+00:00
    End Time: 2025-07-05T19:07:38.453000+00:00
    Total Duration: 4 ms
    Total CPU Time: 0 ms
    Query CPU Time: 0 ms
    Vertipaq CPU Time: 0 ms
    Execution Delay: 0 ms
    Approximate Peak Consumption: 1.0 MiB
    Rows Returned: 5
)

```