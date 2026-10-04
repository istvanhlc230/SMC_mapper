undefined

## ForexFactory HTML parser correction

The live debug result showed that the current ForexFactory range page no longer contains the legacy
embedded days JSON payload. The Calendar acquisition path now falls back to parsing the current
rendered calendar rows, preserving the existing normalized event contract.

The fallback uses the provider event ID, visible date/time, currency, impact, title, actual, forecast,
and previous fields. Event timestamps are converted from the provider-declared Calendar Time Zone,
preferring IANA timezone data and falling back to the declared GMT offset when necessary.
The fallback preserves the existing canonical normalized event schema and provider routing.

Calendar implementation version is now 2.2.1.

A deterministic CI contract test was added for the current HTML row representation and UTC conversion.
The source correction commit is f6eaae3d8c0e453ca6d29f135e050fe74320fb30.
