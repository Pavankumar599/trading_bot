# Binance Futures Testnet Trading Bot (CLI)

A small Python 3 application that places **MARKET**, **LIMIT**, and (bonus) **STOP_MARKET** orders on **Binance USDT-M Futures Testnet** with:
- Clean, reusable structure (API/client layer + CLI layer)
- Input validation
- Logging of requests/responses/errors to a log file
- Robust error handling

> Testnet base URL used: `https://testnet.binancefuture.com`

## Project structure

```
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  cli.py
  requirements.txt
  README.md
  logs/
    sample_market.log
    sample_limit.log
```

## Setup

1) Create & activate a Binance Futures Testnet account and generate API credentials.

2) Create a virtualenv and install dependencies:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

3) Export credentials (recommended):

```bash
export BINANCE_API_KEY="YOUR_KEY"
export BINANCE_API_SECRET="YOUR_SECRET"
```

Windows PowerShell:

```powershell
$env:BINANCE_API_KEY="YOUR_KEY"
$env:BINANCE_API_SECRET="YOUR_SECRET"
```

## Usage

From the repository root:

### Market order (BUY)

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit order (SELL)

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
```

### Bonus: Stop Market order (SELL)

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 75000
```

## Output

The CLI prints:
- Order request summary
- Key response details: `orderId`, `status`, `executedQty`, `avgPrice` (if available)
- Success/failure message

## Logging

Logs are written to:

- `logs/bot.log` (created automatically)

The application logs:
- HTTP method + endpoint
- Request parameters (signature omitted, secrets never logged)
- Response status + JSON body
- Exceptions (network errors, invalid input, API errors)

### Deliverable logs

This repo includes sample log files:
- `logs/sample_market.log`
- `logs/sample_limit.log`

To generate **real** logs for submission:
1. Run at least one MARKET and one LIMIT order command (examples above).
2. Attach `logs/bot.log` with your submission (or copy/rename it).

## Assumptions

- You are using **USDT-M Futures Testnet** at `https://testnet.binancefuture.com`.
- Your account has sufficient testnet funds and the symbol exists on testnet.
- For LIMIT orders we use `timeInForce=GTC`.
- For MARKET orders, `price` is not provided.
- For STOP_MARKET orders, `stopPrice` is required.

## Troubleshooting

- **Timestamp errors / recvWindow**: Ensure your system clock is reasonably accurate. You can increase `recvWindow` in `bot/client.py`.
- **-2019 Margin is insufficient**: Add testnet USDT / ensure correct leverage/margin mode in testnet UI.
- **Symbol not found**: Verify `--symbol` is correct (e.g., `BTCUSDT`).

