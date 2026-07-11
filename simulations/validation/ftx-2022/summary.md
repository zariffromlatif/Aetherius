# Aetherius Backtest Summary - FTX collapse and crypto counterparty contagion (November 2022)

- Event ID: `ftx-2022`
- Commit: `rebuild-gdelt-v3`
- Dataset window: 2022-11-02T00:00:00Z -> 2022-11-14T23:59:59Z
- Observations replayed: 49 | Watchlist size: 4

## Headline metrics

| Metric | Value |
| --- | --- |
| Detection recall | 100% (3/3) |
| Median lead time | 7.12 days (171.0 h) |
| Mapping precision | 100% |
| False positives | 0  |

## Detections (first evidence-backed elevated/high flag per name)

| Ticker | First flag | Realized event | Lead (days) | Severity | Evidence |
| --- | --- | --- | --- | --- | --- |
| COIN | 2022-11-03T21:00:00Z | 2022-11-11T00:00:00Z | 7.12 | high | fool.com: Why Coinbase , Silvergate Capital , and Marathon Digital Holdings Are Falling This Week |
| SBNY | 2022-11-10T11:00:00Z | 2022-11-11T00:00:00Z | 0.54 | elevated | marketwatch.com: Robinhood , Coinbase Distance Themselves from FTX After Crypto Plunge |
| SI | 2022-11-03T21:00:00Z | 2022-11-11T00:00:00Z | 7.12 | high | fool.com: Why Coinbase , Silvergate Capital , and Marathon Digital Holdings Are Falling This Week |

## Honest reading

Measures detection timing and ranking on a frozen historical window. This is early-detection and prioritization evidence, NOT a return forecast or guarantee. Causal-mechanism confidence is not claimed here.
