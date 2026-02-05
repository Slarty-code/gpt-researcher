interface GetHostParams {
  purpose?: string;
}

/** Must match backend default (main.py: PORT env default 8067) */
const DEFAULT_API_BASE = 'http://localhost:8067';

export const getHost = ({ purpose }: GetHostParams = {}): string => {
  if (typeof window !== 'undefined') {
    let { host } = window.location;
    const apiUrlInLocalStorage = localStorage.getItem("GPTR_API_URL");

    const urlParams = new URLSearchParams(window.location.search);
    const apiUrlInUrlParams = urlParams.get("GPTR_API_URL");

    if (apiUrlInLocalStorage) {
      return apiUrlInLocalStorage;
    } else if (apiUrlInUrlParams) {
      return apiUrlInUrlParams;
    } else if (process.env.NEXT_PUBLIC_GPTR_API_URL) {
      return process.env.NEXT_PUBLIC_GPTR_API_URL;
    } else if (process.env.REACT_APP_GPTR_API_URL) {
      return process.env.REACT_APP_GPTR_API_URL;
    } else if (purpose === 'langgraph-gui') {
      return host.includes('localhost') ? 'http%3A%2F%2F127.0.0.1%3A8123' : `https://${host}`;
    } else {
      return host.includes('localhost') ? DEFAULT_API_BASE : `https://${host}`;
    }
  }
  // SSR: no window — use env or default so report links (PDF/DOCX) are absolute and hit the backend
  return process.env.NEXT_PUBLIC_GPTR_API_URL || process.env.REACT_APP_GPTR_API_URL || DEFAULT_API_BASE;
};