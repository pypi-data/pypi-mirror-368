# `bisect`

Perform an evergreen-aware git-bisect to find the 'last passing version' and
'first failing version' of mongo, with respect to a user provided shell script.

## Usage

Help message, usage guide, and list of options:

```bash
db-contrib-tool bisect --help
```

### Cheat Sheet of Common Use Cases

```bash
db-contrib-tool bisect --lookback 5 --branch 6.0 --variant enterprise-ubuntu1804-64 --script /path/to/script/test_bisect.sh
```
