Script to convert tests defined in the Excel file into Robot Framework .robot files.

Each Excel worksheet generates a Robot file.

## How to install

```bash
pip install robot-test-creator
```

## How to use

Basic run - will create .robot files into current directory
```bash
rtc -i tests.xlsx
```
Basic run - will create .robot files into "results" directory
```bash
rtc -i tests.xlsx -o results
```
Prevent title casing given test case and keyword names
```bash
rtc -i tests.xlsx -nt
```


## Examples

Excel Example (tests.xlsx)

![Excel example](excel_example.png)

generated suite1.robot

![Suite1 example](suite1.png)

generated suite2.robot

![Suite2 example](suite2.png)
