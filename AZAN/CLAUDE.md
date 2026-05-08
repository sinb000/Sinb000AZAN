# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AZAN** is an Islamic prayer time notification app built with Expo/React Native (frontend) and FastAPI/MongoDB (backend). It displays prayer times based on GPS location, plays Adhan audio at prayer times, manages custom alarms, and streams Quran radio.

## Commands

### Frontend (`/frontend`)
Uses **Yarn** as the package manager.
```bash
yarn                    # Install dependencies
npx expo start          # Start Expo dev server (Metro bundler)
npx expo start --android  # Launch on Android emulator
npx expo start --ios      # Launch on iOS simulator
npx expo start --web      # Launch in browser
npx expo lint             # Run ESLint
```

### Backend (`/backend`) — first-time setup
Requires **Python 3.11 or 3.12** (3.14 has a broken venv on Windows).

```bash
python -m venv venv
source venv/Scripts/activate        # Git Bash on Windows
grep -v emergentintegrations requirements.txt > requirements_local.txt
pip install -r requirements_local.txt
uvicorn server:app --reload
```

On subsequent runs just activate the venv then start the server:
```bash
source venv/Scripts/activate
uvicorn server:app --reload
```

### Tests
```bash
source backend/venv/Scripts/activate
python backend_test.py        # Run backend integration tests (run from project root)
```

There is no frontend test suite — frontend is validated manually via Expo.

## Architecture

### Data Flow
1. **PrayerContext.tsx** fetches GPS location via `expo-location`, computes prayer times using the `adhan` library (Umm Al-Qura method), and loads/saves user adjustments (per-prayer minute offsets, silent mode flags) to both AsyncStorage and the backend API.
2. **AudioContext.tsx** handles Adhan playback with a three-stage fallback: radio stream → local file from backend → bundled `adhan.mp3` asset. It also manages Quran radio streaming.
3. **Backend (`server.py`)** is a stateless REST API over MongoDB. It stores prayer settings and alarms, and proxies the Quran radio stream to avoid CORS issues on the client.
4. **AudioContext.tsx** polls every 10 seconds to check if the current time matches a prayer time and triggers Adhan playback. It tracks which prayers have already been triggered per day to prevent duplicates.
5. **expo-notifications** schedules silent/sound notifications for each prayer time; the app reschedules these whenever settings change.

### Frontend Structure
- **`app/(tabs)/`** — Tab screens: Home (prayer times display), Prayers (detail), Alarms (CRUD), Settings.
- **`app/adhan-playing.tsx`** — Full-screen modal shown during Adhan playback.
- **`app/alarm-edit.tsx`** — Modal for creating/editing custom alarms.
- **`AudioContext.tsx` / `PrayerContext.tsx`** — App-wide React contexts provided in `app/_layout.tsx`.
- **`utils/prayerCalculations.ts`** — Wraps the `adhan` npm library; applies per-prayer minute adjustments.
- **`types/prayer.ts`** — Shared TypeScript interfaces for prayers, alarms, and settings.
- **`@/*` path alias** — Maps to `frontend/` root (configured in `tsconfig.json`).

### Backend Structure
- **`server.py`** — All endpoints in one file: prayer settings CRUD, alarms CRUD, radio stream proxy, and static Adhan file serving.
- **`backend_test.py`** (project root) — HTTP integration tests covering all backend endpoints.

### Key Libraries
| Purpose | Library |
|---|---|
| Prayer time calculation | `adhan` (npm) |
| File-based routing | `expo-router` |
| Audio playback | `expo-audio`, `expo-av` |
| Local persistence | `@react-native-async-storage/async-storage` |
| Backend framework | FastAPI + motor (async MongoDB) |
| HTTP client (proxy) | httpx |

## Environment Variables

- **`frontend/.env`** — `EXPO_PUBLIC_BACKEND_URL` pointing to the FastAPI server. Must use the machine's LAN IP (e.g. `http://192.168.x.x:8000`), not `localhost`, because Expo runs on a physical device.
- **`backend/.env`** — `MONGO_URL` and `DB_NAME` for MongoDB connection.

## Notes

- Prayer times are calculated **client-side**; the backend does not compute them.
- The app has **no authentication** — the API is open.
- TypeScript is configured in **strict mode** (`frontend/tsconfig.json`).
- The UI and some code comments are bilingual (Arabic/English).
