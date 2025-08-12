import pandas as pd
import string

DANGEROUS_PREFIXES = ("=", "+", "-", "@")

def check_type(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas.DataFrame, got {type(df).__name__}")

def sanitize_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    safe = df.copy()
    for col in safe.columns:
        s = safe[col]
        if pd.api.types.is_string_dtype(s) or s.dtype == object:
            mask = s.notna()
            s_str = s[mask].astype(str)
            s_str = s_str.map(lambda v: "'" + v if v.startswith(DANGEROUS_PREFIXES) else v)
            s = s.copy()
            s.loc[mask] = s_str
            safe[col] = s
    return safe

def df_desc(df: pd.DataFrame) -> pd.DataFrame:
    check_type(df)

    brackets_quotes = set('\'"()[]{}')
    punctuation = set('.,;:!?')
    operators = set('+-*/=%<>')

    all_ascii = set(chr(i) for i in range(128))

    known_ascii = set(string.digits + string.ascii_letters).union(
        brackets_quotes, punctuation, operators, set(' \t\n\r')
    )

    other_ascii = all_ascii - known_ascii

    results = []

    for col in df.columns:
        chars = {
            "numeric": set(),
            "letters_lowercase": set(),
            "letters_uppercase": set(),
            "whitespace": set(),
            "brackets_quotes": set(),
            "punctuation": set(),
            "operators": set(),
            "other_ascii": set(),
            "other_non_ascii": set(),
    	}

        series = df[col].dropna().astype(str)

        for val in series:
            for ch in val:
                if ch.isdigit():
                    chars["numeric"].add(ch)
                elif ch.islower():
                    chars["letters_lowercase"].add(ch)
                elif ch.isupper():
                    chars["letters_uppercase"].add(ch)
                elif ch.isspace():
                    chars["whitespace"].add(ch)
                elif ch in brackets_quotes:
                    chars["brackets_quotes"].add(ch)
                elif ch in punctuation:
                    chars["punctuation"].add(ch)
                elif ch in operators:
                    chars["operators"].add(ch)
                elif ord(ch) < 128 and ch in other_ascii:
                    chars["other_ascii"].add(ch)
                else:
                    chars["other_non_ascii"].add(ch)

        results.append({
            "column": col,
            **{group: "".join(sorted(chars[group])) for group in chars}
        })

    return pd.DataFrame(results)


def df_stats(df: pd.DataFrame) -> pd.DataFrame:
    check_type(df)

    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.shape[1] == 0:
        return pd.DataFrame(columns=["column","min","max","mean","median","std_sample","std_pop"])

    summary = []

    for col in numeric_df.columns:
        values = numeric_df[col].dropna()
        summary.append({
            "column":col,
            "min":values.min(),
            "max":values.max(),
            "mean":values.mean(),
            "median":values.median(),
            "std_sample":values.std(ddof=1),
            "std_pop": values.std(ddof=0)
        })
    
    return pd.DataFrame(summary)


def df_nullique(df: pd.DataFrame) -> pd.DataFrame:
    check_type(df)

    result = []

    for col in df.columns:
        series = df[col]

        cleaned = series.replace(r'^\s*$', '', regex=True)

        is_unique = cleaned.duplicated(keep=False).sum() == 0

        distinct_values = cleaned.fillna("<<NULL>>").replace("", "<<EMPTY>>")
        distinct_count = distinct_values.nunique(dropna=False)

        has_null = cleaned.isnull().any()
        has_empty = (cleaned == "").any()

        if has_null and has_empty:
            null_type = "empty/null"
        elif has_null:
            null_type = "null"
        elif has_empty:
            null_type = "empty"
        else:
            null_type = "filled"
        
        result.append({
            "column": col,
            "is_unique": is_unique,
            "distinct_count": distinct_count,
            "null_type": null_type
        })
    
    return pd.DataFrame(result)