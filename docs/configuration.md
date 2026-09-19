# Configuration

Iyrin uses `config.py`, environment variables, and session-scoped credential controls.

| Environment Variable | Service |
|---|---|
| `GOOGLE_API_KEY` | Google APIs |
| `GOOGLEMAPS_API_KEY` | Google Maps |
| `GOOGLE_WEATHER_API_KEY` | Google Weather |
| `OPENAI_API_KEY` | OpenAI |
| `GEMINI_API_KEY` | Google Gemini |
| `XAI_API_KEY` | Grok / xAI |
| `CLAUDE_API_KEY` | Anthropic Claude |
| `MISTRAL_API_KEY` | Mistral AI |
| `NASA_API_KEY` | NASA APIs |
| `NASA_EARTHDATA_TOKEN` | NASA Earthdata |
| `FIRMS_MAP_KEY` | NASA FIRMS |
| `AIRNOW_API_KEY` | EPA AirNow |
| `OPENAQ_API_KEY` | OpenAQ |
| `PURPLEAIR_API_KEY` | PurpleAir |
| `OPENSKY_CLIENT_ID` | OpenSky OAuth client ID |
| `OPENSKY_API_CLIENT_SECRET` | OpenSky OAuth client secret |
| `AISSTREAM_API_KEY` | AIS Stream |
| `PINECONE_API_KEY` | Pinecone vector storage |

Detailed setup notes remain under `resources/setup/`.

!!! warning "Secrets"
    Do not commit API keys to the repository.
