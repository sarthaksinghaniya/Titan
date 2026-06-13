/**
 * API Configuration Management
 * Centralizes all API-related configuration for dev/prod environments
 */

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelayMs: number;
  debug: boolean;
  environment: "development" | "production";
}

/**
 * Get API configuration based on environment
 * Supports both environment variables and runtime configuration
 */
export function getApiConfig(): ApiConfig {
  const isDev = process.env.NODE_ENV === "development";
  
  // Environment variables take precedence
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  const timeout = process.env.NEXT_PUBLIC_API_TIMEOUT 
    ? parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT)
    : 30000;
  
  return {
    baseUrl: baseUrl ?? (isDev ? "http://localhost:8000" : "/api"),
    timeout,
    retryAttempts: isDev ? 1 : 3,
    retryDelayMs: isDev ? 1000 : 2000,
    debug: isDev,
    environment: isDev ? "development" : "production",
  };
}

/**
 * Get full API endpoint URL with prefix
 * @param path - The API path (e.g., "/api/v1/sessions")
 */
export function getApiUrl(path: string): string {
  const config = getApiConfig();
  return `${config.baseUrl}${path}`;
}

/**
 * Validate API configuration
 * Provides helpful error messages if configuration is incorrect
 */
export function validateApiConfig(): { valid: boolean; errors: string[] } {
  const config = getApiConfig();
  const errors: string[] = [];

  if (!config.baseUrl) {
    errors.push(
      "API base URL is not configured. Set NEXT_PUBLIC_API_URL environment variable or check defaults."
    );
  }

  if (config.timeout < 1000) {
    errors.push("API timeout is too low (< 1000ms). This may cause request failures.");
  }

  if (config.timeout > 120000) {
    errors.push("API timeout is very high (> 120s). Consider reducing for better UX.");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Get human-readable environment description
 */
export function describeApiConfig(): string {
  const config = getApiConfig();
  return `
    API Configuration:
    - Base URL: ${config.baseUrl}
    - Timeout: ${config.timeout}ms
    - Environment: ${config.environment}
    - Debug: ${config.debug}
    - Retry Attempts: ${config.retryAttempts}
  `.trim();
}
