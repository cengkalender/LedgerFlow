# Time policy

LedgerFlow uses timezone-aware datetimes in UTC for domain logic.

## Why

Financial calculations depend on deterministic time values. Domain code must not rely on a local machine time zone or a direct `datetime.now()` call spread across the codebase.

## Clock abstraction

The domain uses a `Clock` protocol to read the current time. This makes tests deterministic and prevents implicit environment-specific behavior.

## UTC policy

All timestamps should be timezone-aware and stored in UTC where possible.

This keeps equality checks and auditing predictable.

## Test use

For deterministic domain tests, use `FakeClock` instead of the system clock.
