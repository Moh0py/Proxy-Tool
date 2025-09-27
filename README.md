# Proxy-Tool

# Proxy Scanner

<div align="center">
 
  <h1>Proxy Scanner</h1>
  <p>A powerful and efficient Python script to fetch, test, and validate free proxies from multiple public sources concurrently.</p>

  <p>
    <a href="#-key-features">Key Features</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-usage">Usage</a> •
    <a href="#-command-line-options">Options</a> •
    <a href="#-workflow">Workflow</a> •
    <a href="#-license">License</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/python-3.6%2B-blue.svg" alt="Python 3.6+">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
  </p>
</div>

---

## 🚀 Key Features

- **Multi-Source Fetching**: Aggregates proxies from a curated list of reliable public sources.
- **Multi-Protocol Support**: Capable of testing `HTTP`, `HTTPS`, `SOCKS4`, and `SOCKS5` proxies.
- **Concurrent Testing**: Utilizes a `ThreadPoolExecutor` to test a large number of proxies in a short amount of time.
- **Performance Metrics**: Accurately measures the latency of each valid proxy in seconds.
- **Flexible CLI**: Easy-to-use command-line interface to customize the scanning process.
- **Dual Export**: Automatically saves valid proxies to both `valid_proxies.txt` and a more detailed `valid_proxies.csv`.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/proxy-scanner.git
    cd proxy-scanner
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install requests tqdm colorama
    ```

## ⚙️ Usage

You can easily run the script from your terminal.

### Basic Usage

To run a scan with the default settings (all proxy types, 40 workers, 8-second timeout):

```bash
python proxy_scanner.py
```

### Advanced Usage

Customize the scan with command-line arguments:

```bash
python proxy_scanner.py --types http,https --workers 50 --timeout 5 --output my_proxies
```

## 📋 Command-Line Options

| Option | Description | Default Value |
| :--- | :--- | :--- |
| `--types` | Comma-separated list of proxy types to test. | `http,https,socks4,socks5` |
| `--workers` | Number of concurrent threads for testing. | `40` |
| `--timeout` | Timeout in seconds for each proxy test request. | `8` |
| `--output` | Base name for the output files (without extension). | `valid_proxies` |
| `--insecure`| Allow insecure SSL requests (disables certificate verification). | `False` |

## 🔄 Workflow

The script follows a simple yet effective workflow:

1.  **Fetch**: Gathers proxy lists from the sources defined in the `SOURCES` dictionary.
2.  **Test**: Concurrently tests each proxy by sending a request to `https://httpbin.org/ip`. A proxy is considered valid if the request is successful (`200 OK`).
3.  **Sort & Save**: Sorts the valid proxies by latency (fastest first) and saves them to the output files.

## 📄 Output Files

Upon completion, the script generates two files:

1.  **`valid_proxies.txt`**: A simple text file where each line contains a valid proxy.
    - **Format**: `ip:port,type,latency`

2.  **`valid_proxies.csv`**: A CSV file with detailed information for each valid proxy, including a header row.
    - **Columns**: `proxy`, `type`, `latency`, `origin`



*© 2025 Mohammad Jabbary*
