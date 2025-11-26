/**
 * Authentication utility functions
 */

const TOKEN_KEY = "access_token";

export const auth = {
    /**
     * Get the stored access token
     */
    getToken(): string | null {
        if (typeof window === "undefined") return null;
        return localStorage.getItem(TOKEN_KEY);
    },

    /**
     * Store the access token
     */
    setToken(token: string): void {
        localStorage.setItem(TOKEN_KEY, token);
    },

    /**
     * Remove the access token
     */
    removeToken(): void {
        localStorage.removeItem(TOKEN_KEY);
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated(): boolean {
        return this.getToken() !== null;
    },

    /**
     * Get authorization headers for API requests
     */
    getAuthHeaders(): HeadersInit {
        const token = this.getToken();
        if (!token) return {};

        return {
            Authorization: `Bearer ${token}`,
        };
    },

    /**
     * Make an authenticated API request
     */
    async fetch(url: string, options: RequestInit = {}): Promise<Response> {
        const headers = {
            ...options.headers,
            ...this.getAuthHeaders(),
        };

        const response = await fetch(url, {
            ...options,
            headers,
        });

        // If unauthorized, redirect to login
        if (response.status === 401) {
            this.removeToken();
            if (typeof window !== "undefined") {
                window.location.href = "/login";
            }
        }

        return response;
    },

    /**
     * Logout user
     */
    logout(): void {
        this.removeToken();
        if (typeof window !== "undefined") {
            window.location.href = "/login";
        }
    },
};
