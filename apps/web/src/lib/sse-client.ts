/**
 * SSE Connection utility for TITAN.
 *
 * Hardening changes (Step 7.1):
 * - Tracks `isIntentionallyClosed` so that disconnect() does not trigger
 *   the error handler's reconnect logic — preventing a reconnect loop
 *   after session_complete.
 * - Reconnect attempts are reset on successful open so a transient
 *   network hiccup doesn't permanently exhaust the retry budget.
 * - Exposes `isIntentionallyClosed` so callers can inspect the state.
 */
import type { SSEEvent, SSEEventType } from '@titan/shared-types';

type SSEHandler<T = unknown> = (event: SSEEvent<T>) => void;
type ErrorHandler = (error: Error) => void;

export interface SSEConnectionOptions {
  onEvent?: SSEHandler;
  onError?: ErrorHandler;
  onClose?: () => void;
  handlers?: Partial<Record<SSEEventType, SSEHandler<never>>>;
}

export class SSEConnection {
  private eventSource: EventSource | null = null;
  private url: string;
  private options: SSEConnectionOptions;
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts = 3;
  /** True when disconnect() was called intentionally (not due to an error). */
  private isIntentionallyClosed = false;

  constructor(url: string, options: SSEConnectionOptions = {}) {
    this.url = url;
    this.options = options;
  }

  connect(): void {
    if (this.eventSource) {
      this.disconnect();
    }

    this.isIntentionallyClosed = false;
    this.eventSource = new EventSource(this.url);

    this.eventSource.onopen = () => {
      // Reset retry counter on successful open so transient errors
      // don't permanently exhaust the reconnect budget.
      this.reconnectAttempts = 0;
    };

    this.eventSource.onmessage = (event: MessageEvent<string>) => {
      try {
        const parsed = JSON.parse(event.data) as SSEEvent;
        this.options.onEvent?.(parsed);

        const specificHandler = this.options.handlers?.[parsed.event];
        if (specificHandler) {
          specificHandler(parsed as SSEEvent<never>);
        }

        // Close intentionally on terminal events so the reconnect logic
        // is not triggered by the subsequent onerror that fires on close.
        if (parsed.event === 'session_complete' || parsed.event === 'error') {
          this.disconnect();
        }
      } catch {
        console.error('[SSE] Failed to parse event:', event.data);
      }
    };

    this.eventSource.onerror = () => {
      // Do not reconnect if we closed intentionally (session done).
      if (this.isIntentionallyClosed) return;

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = 1000 * this.reconnectAttempts;
        console.warn(`[SSE] Connection error — retrying in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => {
          if (!this.isIntentionallyClosed) {
            this.connect();
          }
        }, delay);
      } else {
        this.options.onError?.(
          new Error('SSE connection failed after max retries')
        );
        this.disconnect();
      }
    };
  }

  disconnect(): void {
    this.isIntentionallyClosed = true;
    this.eventSource?.close();
    this.eventSource = null;
    this.options.onClose?.();
  }

  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

export function createSSEConnection(
  sessionId: string,
  options: SSEConnectionOptions = {}
): SSEConnection {
  const isServer = typeof window === 'undefined';
  const apiUrl = isServer
    ? (process.env.INTERNAL_API_URL ??
       process.env.NEXT_PUBLIC_API_URL ??
       'http://localhost:8000')
    : ''; // Browser: relative path through Next.js proxy
  const url = `${apiUrl}/api/v1/sessions/${sessionId}/stream`;
  return new SSEConnection(url, options);
}
