# Aetherius Backtest Summary - Silicon Valley Bank collapse and regional-bank contagion (March 2023)

- Event ID: `svb-2023`
- Commit: `rebuild-gdelt-v2`
- Dataset window: 2023-03-06T00:00:00Z -> 2023-03-12T23:59:59Z
- Observations replayed: 98 | Watchlist size: 6

## Headline metrics

| Metric | Value |
| --- | --- |
| Detection recall | 100% (5/5) |
| Median lead time | 2.34 days (56.2 h) |
| Mapping precision | 100% |
| False positives | 0  |

## Detections (first evidence-backed elevated/high flag per name)

| Ticker | First flag | Realized event | Lead (days) | Severity | Evidence |
| --- | --- | --- | --- | --- | --- |
| FRC | 2023-03-09T17:45:00Z | 2023-03-13T00:00:00Z | 3.26 | high | fool.com: Why Shares of First Republic Bank Are Falling Today |
| PACW | 2023-03-10T15:45:00Z | 2023-03-13T00:00:00Z | 2.34 | elevated | investors.com: Silicon Valley Bank Trading Halted , Company Seeks Buyer , Financial Stocks Shudder |
| SBNY | 2023-03-09T12:30:00Z | 2023-03-12T00:00:00Z | 2.48 | high | marketwatch.com: Signature Bank stock drops sharply after Silvergate announces winddown |
| SIVB | 2023-03-09T13:00:00Z | 2023-03-10T00:00:00Z | 0.46 | high | marketwatch.com: SVB Financial stock plummets toward biggest one - day selloff in 23 years after stock offering , large losses on securities sales |
| WAL | 2023-03-10T15:45:00Z | 2023-03-13T00:00:00Z | 2.34 | elevated | investors.com: Silicon Valley Bank Trading Halted , Company Seeks Buyer , Financial Stocks Shudder |

## Honest reading

Measures detection timing and ranking on a frozen historical window. This is early-detection and prioritization evidence, NOT a return forecast or guarantee. Causal-mechanism confidence is not claimed here.
