import { ApiError } from "../types/api";

function getCookie(name: string): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const cookies = `; ${document.cookie}`;
  const parts = cookies.split(`; ${name}=`);

  if (parts.length !== 2) {
    return null;
  }

  return parts.pop()?.split(";").shift() || null;
}

export class ApiClientError extends Error {
  code: string;

  constructor(message: string, code: string) {
    super(message);
    this.code = code;
    this.name = "ApiClientError";
  }
}

type SessionResponse = {
  authenticated: boolean;
  user: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  } | null;
};

let sessionPromise: Promise<SessionResponse> | null = null;

/**
 * Establish the Django browser session.
 *
 * IMPORTANT:
 * On the browser we deliberately use the Next.js relative URL:
 *
 * /api/auth/session/
 *
 * This makes the browser receive and retain the Django
 * sessionid + csrftoken cookies under localhost:3000.
 */
async function bootstrapSession(): Promise<SessionResponse> {
  if (typeof window === "undefined") {
    throw new ApiClientError(
      "Session bootstrap must run in the browser.",
      "SESSION_BROWSER_REQUIRED",
    );
  }

  if (!sessionPromise) {
    sessionPromise = fetch("/api/auth/session/", {
      method: "GET",
      credentials: "include",
      cache: "no-store",
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new ApiClientError(
            "Unable to establish the learner session.",
            "SESSION_BOOTSTRAP_FAILED",
          );
        }

        const data = (await response.json()) as SessionResponse;

        if (!data.authenticated) {
          throw new ApiClientError(
            "Learner session was not authenticated.",
            "UNAUTHORIZED",
          );
        }

        return data;
      })
      .catch((error: unknown) => {
        if (error instanceof ApiClientError) {
          throw error;
        }

        throw new ApiClientError(
          error instanceof Error
            ? error.message
            : "Unable to establish learner session.",
          "SESSION_BOOTSTRAP_FAILED",
        );
      })
      .finally(() => {
        sessionPromise = null;
      });
  }

  return sessionPromise;
}

/**
 * Make an API request.
 *
 * Browser flow:
 *
 *   bootstrap session
 *        ↓
 *   browser stores sessionid/csrftoken
 *        ↓
 *   request /api/path/
 *        ↓
 *   Next.js proxy
 *        ↓
 *   Django
 *
 * This prevents the Home page from requesting /api/path/
 * before authentication cookies exist.
 */
async function request<T>(
  url: string,
  options: RequestInit = {},
  isRetry = false,
): Promise<T> {
  const isServer = typeof window === "undefined";
  const isSessionRequest = url.includes("/api/auth/session/");

  /*
   * IMPORTANT:
   * Browser requests MUST use relative /api/... URLs.
   *
   * This allows the browser to communicate with the Next.js
   * proxy on localhost:3000 and retain Django session cookies.
   */
  const targetUrl = isServer
    ? `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}${url}`
    : url;

  /*
   * GUARANTEE SESSION BEFORE NORMAL BROWSER REQUESTS.
   *
   * This is the key fix.
   *
   * Even if AuthProvider and page.tsx execute at nearly the
   * same time, getPath(), getStats(), getProfile(), etc.
   * cannot run until the browser session has been established.
   */
  if (!isServer && !isSessionRequest) {
    await bootstrapSession();
  }

  const headers = new Headers(options.headers || {});

  /*
   * JSON content type for JSON request bodies.
   */
  if (
    options.body &&
    !headers.has("Content-Type") &&
    !(options.body instanceof FormData)
  ) {
    headers.set("Content-Type", "application/json");
  }

  /*
   * Django CSRF protection.
   *
   * The csrftoken cookie is created by /api/auth/session/.
   * We read it immediately before every mutating request.
   */
  if (
    !isServer &&
    options.method &&
    options.method.toUpperCase() !== "GET"
  ) {
    const csrfToken = getCookie("csrftoken");

    if (csrfToken) {
      headers.set("X-CSRFToken", csrfToken);
    }
  }

  const config: RequestInit = {
    ...options,
    headers,
    credentials: "include",
    cache: "no-store",
  };

  try {
    const response = await fetch(targetUrl, config);

    /*
     * If the Django session expired unexpectedly:
     *
     * 401
     * ↓
     * bootstrap session again
     * ↓
     * retry original request once
     */
    if (
      response.status === 401 &&
      !isRetry &&
      !isSessionRequest &&
      !isServer
    ) {
      await bootstrapSession();

      return request<T>(url, options, true);
    }

    let data: unknown = null;

    const contentType = response.headers.get("content-type");

    if (
      contentType &&
      contentType.toLowerCase().includes("application/json")
    ) {
      data = await response.json();
    }

    if (!response.ok) {
      const apiData = data as {
        error?: {
          code?: string;
          message?: string;
        };
      } | null;

      if (apiData?.error) {
        throw new ApiClientError(
          apiData.error.message || "API request failed.",
          apiData.error.code || "INVALID_REQUEST",
        );
      }

      throw new ApiClientError(
        response.statusText || "An unexpected error occurred.",
        response.status === 401
          ? "UNAUTHORIZED"
          : "INVALID_REQUEST",
      );
    }

    return data as T;
  } catch (error: unknown) {
    if (error instanceof ApiClientError) {
      throw error;
    }

    throw new ApiClientError(
      error instanceof Error
        ? error.message
        : "Network error.",
      "NETWORK_ERROR",
    );
  }
}

export const apiClient = {
  get: <T>(
    url: string,
    options?: RequestInit,
  ): Promise<T> =>
    request<T>(
      url,
      {
        ...options,
        method: "GET",
      },
    ),

  post: <T>(
    url: string,
    body?: unknown,
    options?: RequestInit,
  ): Promise<T> =>
    request<T>(
      url,
      {
        ...options,
        method: "POST",
        body:
          body !== undefined
            ? JSON.stringify(body)
            : undefined,
      },
    ),
};