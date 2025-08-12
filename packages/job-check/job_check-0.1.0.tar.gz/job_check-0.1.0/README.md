# JobSpy Runner (CLI)

JobSpy Runner is a CLI tool for scraping job listings (e.g. LinkedIn) using the `jobspy` library, with proxy rotation and CSV export.

## Features
- Proxy rotation
- CSV export (optionally numbered)
- Simple CLI interface

## Installation & Setup
You MUST Use a Python virtual environment.

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required modules
pip install -r requirements.txt
```

# Approach 1: Executable

The compiled executable can be found in your project folder:
`dist/jobspy-runner`

To run the executable, use:
```bash
./dist/jobspy-runner --search "Software Engineer" --location "New York"
```

If you want to run it from the project root, you can also copy or symlink it:
```bash
cp dist/jobspy-runner ./jobspy-runner
./jobspy-runner --search "Software Engineer" --location "New York"
```

You can also use optional arguments, for example:
```bash
./jobspy-runner -s linkedin indeed -r 20 -n -o jobs.csv -d
```

## Approach 2: Terminal Command
Run the CLI with required arguments:
```bash
python3 jobspy_runner/cli.py --search "Software Engineer" --location "New York"
```


Optional arguments:

Optional arguments (short flags available):
- `--sites`, `-s` linkedin indeed (default: linkedin)
- `--results`, `-r` 20 (default: 10)
- `--proxies`, `-p` <your_proxies_file> (default: Proxies/proxies_list.txt)
- `--numbered`, `-n` (write numbered CSV)
- `--out`, `-o` jobs.csv (output path)
- `--description`, `-d` (fetch description text; no description by default)

See all options:
```bash
python jobspy_runner/cli.py --help
```

## Proxy Setup
1. Add proxies to `Proxies/proxies_list.txt` (one per line).
2. Test proxies:
   ```bash
   python Proxies/proxies_test.py
   ```
3. Use `Proxies/working_proxies.txt` for scraping.

## Project Structure
```
jobspy_runner/cli.py      # CLI entry point
Proxies/                  # Proxy list & tester
requirements.txt          # Python dependencies
pyproject.toml            # Project metadata
```

## Notes
- Respect site Terms of Service.
- Use responsible scraping intervals.

## License
See LICENSE file.
