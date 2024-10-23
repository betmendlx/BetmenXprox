# BetmenXprox 🦇

A powerful and efficient proxy hunter and checker tool that collects HTTP, SOCKS4, and SOCKS5 proxies from multiple sources and verifies their functionality.

![BetmenXprox Banner](https://raw.githubusercontent.com/betmendlx/betmenxprox/main/banner.png)

## Features ✨

- Collects proxies from 40+ reliable sources
- Supports HTTP, SOCKS4, and SOCKS5 proxies
- Multi-threaded proxy checking (100 threads)
- Beautiful CLI interface with colorful output
- Automatic duplicate removal and proxy normalization
- Process locking to prevent multiple instances
- Organized output files for valid proxies
- Runtime tracking and statistics

## Prerequisites 📋

The following packages are required:

```bash
sudo apt-get install figlet lolcat
```

Python dependencies:
- httpx
- colorama
- psutil

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/betmendlx/betmenxprox.git
cd betmenxprox
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage 💻

Run the script:
```bash
python3 betmenXprox-v4.py
```

The script will:
1. Download proxies from multiple sources
2. Remove duplicates and normalize formats
3. Check proxy functionality
4. Save working proxies to separate files based on type:
   - `valid.http.txt`
   - `valid.socks4.txt`
   - `valid.socks5.txt`

## Output Files 📁

- `http.txt`: Raw HTTP proxies
- `socks4.txt`: Raw SOCKS4 proxies
- `socks5.txt`: Raw SOCKS5 proxies
- `valid.http.txt`: Working HTTP proxies
- `valid.socks4.txt`: Working SOCKS4 proxies
- `valid.socks5.txt`: Working SOCKS5 proxies

## Process Management 🔄

- The script uses a lock file system to prevent multiple instances
- Previous instance information is displayed if already running
- Runtime statistics are tracked and displayed

## Contributing 🤝

Contributions are welcome! Here's how you can help:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Credits 👏

- Proxy sources from various public repositories
- Built with assistance from AI
- Thanks to all contributors who maintain the proxy lists

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer ⚠️

This tool is for educational purposes only. Make sure to comply with all applicable laws and terms of service when using proxies.

## Support 💪

If you find this tool useful, please consider giving it a star ⭐ on GitHub!

For issues, bugs, or feature requests, please [open an issue](https://github.com/betmendlx/betmenxprox/issues).
