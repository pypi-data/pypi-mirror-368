### IDOR Finder

Powerful IDOR discovery tool with UUID-aware fuzzing, parameter extraction, async engine, and HTML/CSV/JSON reports.

### Install

```bash
pip install idor-finder
```

### Usage

```bash
idor-finder https://target/app?user_id=123 --method GET --report-format html --wordlist idor_finder/data/idor_wordlist.txt --sensitive idor_finder/data/sensitive_keywords.txt
```

From file:

```bash
idor-finder --url-file urls.txt --auth-config idor_finder/examples/config_example.json --report-format json
```

### Features

- Extracts parameters from query strings, paths (numeric, UUID), forms, JSON bodies
- Generates numeric sequences, high IDs, and realistic UUID alternatives
- Async fuzz engine with concurrency and rate limiting
- Matches by status anomalies, content length deltas, and sensitive keywords
- Exports HTML, CSV, and JSON reports

### Notes

- Provide your own authentication config in `examples/config_example.json`.
- Wordlist in `data/idor_wordlist.txt` is normalized and expanded at runtime.


