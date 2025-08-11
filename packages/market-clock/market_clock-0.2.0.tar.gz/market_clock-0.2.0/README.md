# Market Clock

Market Clock is a minimalistic command-line clock that tracks the current trading status of multiple stock exchanges worldwide. It uses the released trading holidays to determine whether the markets are open or closed and counts down to the next trading event. 

![](/screenshots/screen.png)

## Table of Contents
- [Features](#features)
- [Supported Markets](#supported-markets)
- [Installation](#installation)
- [Supported Markets](#supported-markets)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Displays trading status for major global stock exchanges.
- Accounts for holidays and half trading days.
- Considers lunch breaks for exchanges with lunch hours.
- Real-time updates on when each market will open or close.

## Supported Markets

Market Clock currently supports the following exchanges:

| Exchange                      | Updated till| Source | Note|
|-------------------------------|-------------|--------|-----|
| TSE (Tokyo Stock Exchange)    | 2026 EOY    | [TSE](https://www.jpx.co.jp/english/corporate/about-jpx/calendar/)||
| SSE (Shanghai Stock Exchange) | 2025 EOY    | [SSE](https://english.sse.com.cn/start/trading/schedule/)||
| HKEX (Hong Kong Exchange)     | 2025 EOY    | [HKEX](https://www.hkex.com.hk/Services/Trading-hours-and-Severe-Weather-Arrangements/Trading-Hours/Securities-Market) ||
| BSE (Bombay Stock Exchange)   | 2025 EOY    | [BSE](https://www.bseindia.com/static/markets/marketinfo/listholi.aspx)| Note that [Muhurat trading](https://en.wikipedia.org/wiki/Muhurat_trading) is currently not supported.|
| LSE (London Stock Exchange)   | 2026 EOY    | [LSE](https://www.londonstockexchange.com/equities-trading/business-days)||
| NYSE (New York Stock Exchange)| 2027 EOY    | [NYSE](https://www.nyse.com/markets/hours-calendars)||
| Nasdaq| 2025 EOY    | [Nasdaq](https://www.nasdaq.com/market-activity/stock-market-holiday-schedule)||

## Installation

`uv` is needed. Install it if you haven't:

```bash
pip install uv
```

To use Market Clock, install it as a uv tool:

```bash
uv tool install market-clock
market-clock
```

or you can invoke it without installing:

```bash
uvx market-clock
```

To exit the application, simply press `Ctrl + C`.

## Usage

Market Clock supports several command line arguments to customize its behavior:

`-m`, `--markets`: Specify which market(s) to display. For example, to show only NYSE and Nasdaq:

```bash
uvx market-clock --markets NYSE Nasdaq
```

  If no market is specified, it will display the status for all supported markets.

`-s`, `--show-seconds`: Display seconds in the countdown timer. By default, seconds are hidden.

```bash
uvx market-clock --show-seconds
```

`-lm`, `--list-markets`: List all supported markets without starting the clock.

```bash
uvx market-clock --list-markets
```

`-p`, `--print`: Print the clock and exit immediately.

```bash
uvx market-clock --print
```

## Contributing

Contributions are welcome! Please fork the repository and create a new branch for your feature or bug fix.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

--- 
