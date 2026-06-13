# Investigation Report — Axios Network Error & Monorepo Connectivity Audit

This report documents the exact root causes, affected files, and recommended fix plan for the "AxiosError: Network Error" and related connection issues within the monorepo.

---

## 1. Root Cause Analysis

We identified four core networking and configuration issues that combine to cause Axios Network Errors, 404s, and EventSource connection failures:

### A. URL Suffix Mismatch (`/api/v1`)
- **API Base URL**: In `api.ts`, the base URL is defined as `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'`. Since `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000` in `.env.local`, the fallback is ignored, and the base URL resolves to `http://localhost:8000`.
- **Request Endpoint**: The frontend calls `api.post('/sessions')` (expecting the `/api/v1` prefix to be in the base URL). Because of the mismatch, Axios requests `http://localhost:8000/sessions`, which does not exist (the backend expects `/api/v1/sessions`).
- **SSE Stream**: A similar issue occurs in `useEventStream.ts`, where the EventSource URL evaluates to `http://localhost:8000/sessions/${projectId}/stream` instead of `http://localhost:8000/api/v1/sessions/${projectId}/stream`.

### B. Docker Container-to-Container Mismatch (SSR & Proxy)
- **Localhost vs Container Host**: Inside `docker-compose.yml`, the frontend container environment variable `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000`.
- **SSR Failure**: When Next.js executes Server-Side Rendering (SSR) or routes proxy rewrites on the server side, it tries to connect to `http://localhost:8000`. However, inside the `web` container, port `8000` is not listening; the API is located at `http://api:8000`. This causes an immediate server-side connection refusal/timeout.

### C. Hardcoded Localhost & CORS Constraints
- The backend CORS middleware allows origins from `ALLOWED_ORIGINS`. If the client connects from an external host/IP (e.g. mobile device testing or staging), CORS blocks the request because the origins do not match `http://localhost:3000`. 
- **Recommendation**: Route client-side requests through relative URLs to use the Next.js reverse proxy rewrite rules. This handles origin routing through port `3000` natively and bypasses browser CORS issues.

### D. CORS Env Configuration Crash
- The Pydantic model configuration in `apps/api/app/core/config.py` expects a strict JSON list for `ALLOWED_ORIGINS` (`List[str]`). If the `.env` file uses a standard comma-separated string (`http://localhost:3000,http://localhost:3001`), the backend application fails to parse it and crashes on startup.

---

## 2. List of Affected Files

### Frontend (`apps/web`)
1. [api-client.ts](file:///c:/Users/LOQ/Desktop/TITAN/apps/web/src/lib/api-client.ts) (Axios client setup, needs base URL auto-detection and retry logic)
2. [api.ts](file:///c:/Users/LOQ/Desktop/TITAN/apps/web/src/lib/api.ts) (Redundant/duplicate client instance with mismatched base path)
3. [page.tsx](file:///c:/Users/LOQ/Desktop/TITAN/apps/web/src/app/page.tsx) (Home page using old `api` instead of centralized client)
4. [sse-client.ts](file:///c:/Users/LOQ/Desktop/TITAN/apps/web/src/lib/sse-client.ts) (EventSource SSE client, needs path correction)
5. [useEventStream.ts](file:///c:/Users/LOQ/Desktop/TITAN/apps/web/src/hooks/useEventStream.ts) (EventSource stream connection hook, needs path correction)
6. [next.config.ts](file:///c:/Users/LOQ/Desktop/TITAN/apps/web/next.config.ts) (Proxy configuration, needs standalone build mode and internal server API URL)

### Backend (`apps/api`)
7. [config.py](file:///c:/Users/LOQ/Desktop/TITAN/apps/api/app/core/config.py) (CORS config validator)

### Infrastructure & Configs
8. [docker-compose.yml](file:///c:/Users/LOQ/Desktop/TITAN/docker/docker-compose.yml) (Needs `INTERNAL_API_URL: http://api:8000` mapping)

---

## 3. Recommended Fix Plan

1. **Centralize & Harden API Client**:
   - Merge `api.ts` and `api-client.ts`.
   - Resolve `baseURL` dynamically: relative (`""`) on the client to leverage Next.js reverse proxy rewrites; absolute (`INTERNAL_API_URL` or `NEXT_PUBLIC_API_URL`) on the server.
   - Add a response interceptor with exponential backoff retry logic (up to 3 attempts) for transient errors (timeouts, network drops, 503s).
2. **Standardize Endpoints**:
   - Correct EventSource URL constructions to consistently include the `/api/v1` route prefix.
3. **Align Docker & Rewrite Networking**:
   - Map `INTERNAL_API_URL` in `docker-compose.yml` to the `web` container.
   - Configure Next.js rewrites in `next.config.ts` to forward server-side requests to `INTERNAL_API_URL`.
4. **Harden Backend Config**:
   - Add a Pydantic `@field_validator` in `config.py` to parse allowed origins flexibly from both comma-separated and JSON string lists.
