# df-this
---
Every enjoyed ever-changing data incoming? Not knowing what to expect in Excel files coming from *'trusted'* sources? Rumours talking about **distinct columns** or no **nan/null/empty** values?

### Welcome to your solution: ***df-this***

---

## What are you talking about exactly?

df-this is a library with 3 small functions to quickly check your dataframe in your code or any incoming Excel file using CLI commands. It will break down your dataframe and give you basic insights about what to expect from your data. But before we come to the main idea of this library, let me explain to you the 2 minor add-on functions first!

### df_stats() | CLI: df-this --stat input.xlsx output_name

This will simply check for numeric columns and give you a basic statistical summary for each column:
- Minimum value
- Maximum value
- Mean (average)
- Median
- Sample standard deviation (ddof=1)
- Population standard deviation (ddof=0)

*When using the CLI command it will save the created summary as an Excel file with output_name as path (if not given an output_name it will save it under a default name). The python function simply returns the summary as dataframe.*


### df_nullique() | CLI: df-this --null input.xlsx output_name

Basically profiles the uniqueness, distinctness, and missingness of each column in the dataframe. For each column:
- Determines if all values are unique
- Counts the number of distinct values, treating null and empty strings as distinct categories
- Classifies the type of missing data
    - "null" if only NaN/None values are present
    - "empty" if only empty strings are present
    - "empty/null" if both are found
    - "filled" if neither are present

*When using the CLI command it will save the created summary as an Excel file with output_name as path (if not given an output_name it will save it under a default name). The python function simply returns the summary as dataframe.*


### df_desc() | CLI: df-this --desc input.xlsx output_name

This function is the main reason this library exists. It analyzes the character composition of each column in a dataframe. For every column, it scans all non-null cell values (after converting to string) and identifies which types of characters appear, including:
- Numeric digits
- Lowercase letters
- Uppercase letters
- Whitespace characters
- Brackets and quotation marks
- Punctuation symbols
- Mathematical/logic operators
- Other ASCII characters
- Non-ASCII characters

*When using the CLI command it will save the created summary as an Excel file with output_name as path (if not given an output_name it will save it under a default name). The python function simply returns the summary as dataframe.*

---

## The full CLI command:
### CLI: df-this --all input.xlsx output_name

This will take the input.xlsx file, create 3 additional sheets for each function and save the original Excel sheet with the 3 additional sheets under the output_name (if not given an output_name it will save it under a default name). THIS IS NOT AVAILABLE AS A PYTHON FUNCTION.

---

Published under Apache 2.0 - (See LICENSE file)

**If you have any recommendations/wishes, let me know.**

---

Version 0.1.0: First release of this library. Contains 3 functions and CLI support for Excel files.