import type { SSEEvent, SSEEventType } from "@titan/shared-types";

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
  private maxReconnectAttempts = 3;

  constructor(url: string, options: SSEConnectionOptions = {}) {
    this.url = url;
    this.options = options;
  }

  connect(): void {
    if (this.eventSource) {
      this.disconnect();
    }

    this.eventSource = new EventSource(this.url);

    this.eventSource.onmessage = (event: MessageEvent) => {
      try {
        const parsed = JSON.parse(event.data as string) as SSEEvent;
        this.options.onEvent?.(parsed);

        const specificHandler = this.options.handlers?.[parsed.event];
        if (specificHandler) {
          specificHandler(parsed as SSEEvent<never>);
        }
      } catch {
        console.error("[SSE] Failed to parse event:", event.data);
      }
    };

    this.eventSource.onerror = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
      } else {
        this.options.onError?.(new Error("SSE connection failed after max retries"));
        this.disconnect();
      }
    };
  }

  disconnect(): void {
    this.eventSource?.close();
    this.eventSource = null;
    this.options.onClose?.();
  }

  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

export function createSSEConnection(sessionId: string, options: SSEConnectionOptions = {}): SSEConnection {
  const isServer = typeof window === "undefined";
  const apiUrl = isServer
    ? (process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    : ""; // Browser uses relative path to go through Next.js proxy
  const url = `${apiUrl}/api/v1/sessions/${sessionId}/stream`;
  return new SSEConnection(url, options);
}
