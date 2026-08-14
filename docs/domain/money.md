# Money domain model

LedgerFlow stores financial values as integer minor units instead of floats.

## Why minor units?

Using floats for money introduces rounding errors. For example, 100.10 + 20.20 may produce unexpected decimals in binary floating-point arithmetic.

LedgerFlow stores amounts in minor units, such as kuruş for TRY.

Examples:

- 125.50 TRY -> 12550
- 10.00 TRY -> 1000

This makes arithmetic deterministic and safe.

## Currency rules

Every money value has an explicit currency. Arithmetic is only valid when the currencies match.

Examples:

- Money(1000, Currency("TRY")) + Money(500, Currency("TRY")) -> valid
- Money(1000, Currency("TRY")) + Money(500, Currency("USD")) -> raises CurrencyMismatchError

## Immutable value object

Money is a frozen dataclass and should not be mutated after creation.

## Assumptions

This domain model does not include conversion rates. Currency conversion is intentionally out of scope for the initial domain foundation.
