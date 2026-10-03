# SMC Monitor Specification

Status: Current implementation specification.

Canonical authority remains .agents/skills/smc/. This document defines runtime orchestration, scheduling, alerting, and process boundaries.

## 0. Calendar ownership

Calendar acquisition, provider resolution, normalization, watermarks, coverage, deduplication, and calendar.json persistence belong to:

    calendar.py
    specifications/calendar_specification.md

Monitor owns:
- scheduling;
- process orchestration;
- current-price observation;
- session context;
- News warning policy;
- target/RR evaluation;
- alerting;
- transient state.

Monitor never calls ForexFactory or Yahoo directly.

## 1. Runtime dependency

    market_data.py
          |
    marketdata JSON
          |
    smc_mapper.py
          |
    structures JSON

    Calendar Update Engine
          |
    <DATA_ROOT>/calendar.json
          |
        Monitor

Calendar update work is outside the canonical candle-close critical path.

## 2. General cycle

    discover/load analyses
          |
    plan Market Data ranges
          |
    invoke Market Data
          |
    reload Market Data
          |
    invoke affected Mapper analyses
          |
    reload Structures
          |
    refresh current market reference
          |
    request Calendar update asynchronously
          |
    read committed local calendar.json
          |
    evaluate News warning
          |
    evaluate targets/RR/alerts
          |
    schedule next cycle

Calendar completion is never a prerequisite for canonical Market Data or Mapper processing.

## 3. Dynamic News horizon

For each stored analysis:

    base_window = duration(entry_timeframe)

    HIGH   -> base_window * 2
    MEDIUM -> base_window
    LOW    -> base_window / 2
    UNKNOWN / HOLIDAY -> no warning

The timeframe duration comes from the existing Market Data timeframe-duration contract.

Acquisition horizon:

    max_news_horizon =
        max(duration(entry_timeframe) * 2)

The Monitor plans coverage from the current UTC date through the UTC date containing now + max_news_horizon.

## 4. Planning function

    def plan_news_acquisition(
        symbol: str,
        analysis_views: list[StoredAnalysisView],
        now: datetime,
    ) -> tuple[date, date] | None:
        ...

The result is converted to an explicit Calendar range:

    python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD

No old relative scopes are used.

No next evaluation exists.

## 5. Asynchronous Calendar dispatch

Required boundary:

    def request_calendar_update_async(
        symbol: str,
        scope: str,
        debug: bool = False,
    ) -> None:
        ...

The Monitor starts calendar.py as a non-blocking subprocess.

It must not:
- wait for provider completion;
- parse provider stdout as canonical data;
- parse provider HTML/JSON;
- write calendar.json.

The Monitor may retain a transient process handle for diagnostics.

Allowed launches:

    python calendar.py SYMBOL YYYY.MM.DD
    python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
    python calendar.py SYMBOL current

## 6. Incremental refresh

A background incremental request uses:

    python calendar.py SYMBOL current

This requires existing provider+canonical-symbol watermarks.

Monitor must never invent a bootstrap timestamp.

Initial bootstrap is performed through an explicit date or datetime-range request.

## 7. Local Calendar read

After dispatching an update, Monitor reads the currently committed:

    <DATA_ROOT>/calendar.json

The read is local and network-free.

If an update has not completed, Monitor uses the last committed valid snapshot and continues.

## 8. Symbol filtering

HUF:
- ForexFactory economic events where details.currency == HUF.

USDHUF:
- ForexFactory events for USD or HUF;
- Yahoo news whose canonical symbol is USDHUF.

NVDA:
- Yahoo news whose canonical symbol is NVDA.

Provider-wide ForexFactory ALL is not implicitly duplicated into standalone currency results.

## 9. Availability states

Monitor distinguishes:

    VALID_DATA
    NO_DATA
    PARTIAL
    UNAVAILABLE
    BOOTSTRAP_REQUIRED

These states are not collapsed into "no event".

Calendar unavailability does not block Market Data or Mapper processing.

## 10. Warning eligibility

The dynamic HIGH/MEDIUM/LOW formula applies only to ForexFactory economic events.

Eligibility:

    0 < (event_time_utc - now_utc) <= warning_window

Yahoo news is not warning-eligible by default.

Monitor must not infer severity from Yahoo publisher, title, URL, category, or source.

## 11. Runtime event status

Economic-event runtime observation remains:

    UPCOMING
    ONGOING
    ENDED

Event end convention:

    event_end_time =
        event_time + duration(analysis.entry_timeframe)

These statuses are Monitor observations only.

They do not alter canonical SMC state, POI lifecycle, mapper checkpoints, or Calendar persistence.

## 12. Calendar failure isolation

Calendar provider failure, update-process failure, timeout, or missing cache:
- never advances a Mapper checkpoint;
- never changes canonical SMC state;
- never blocks Market Data/Mapper work;
- suppresses News warning only because validated event facts are unavailable.

## 13. Definition of done

Acceptance requires:
1. Calendar network I/O is never performed synchronously in the candle-close path.
2. Calendar update is launched asynchronously.
3. Only explicit date/datetime/current forms are referenced.
4. next is not referenced.
5. current is understood only as watermark-based incremental update.
6. Monitor reads only normalized local Calendar data.
7. Yahoo news has no invented warning severity.
8. Provider failures remain observable.
9. Future warning coverage is requested with explicit date-range syntax.
