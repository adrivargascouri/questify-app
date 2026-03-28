/**
 * API Module - Handles all HTTP requests to the backend
 */

class API {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                credentials: 'same-origin'
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Not authenticated - redirect to login
                    window.location.href = '/login';
                    return;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // ===== TASKS API =====

    /**
     * Get all tasks for current user
     */
    async getTasks() {
        return this.request('/api/tasks', { method: 'GET' });
    }

    /**
     * Create a new task
     */
    async createTask(title, description = '', difficulty = 'medium', category = 'general') {
        return this.request('/api/tasks', {
            method: 'POST',
            body: JSON.stringify({ title, description, difficulty, category })
        });
    }

    /**
     * Complete a task
     */
    async completeTask(taskId) {
        return this.request(`/api/tasks/${taskId}/complete`, { method: 'PUT' });
    }

    /**
     * Delete a task
     */
    async deleteTask(taskId) {
        return this.request(`/api/tasks/${taskId}`, { method: 'DELETE' });
    }

    // ===== INVENTORY API =====

    /**
     * Get user's inventory
     */
    async getInventory() {
        return this.request('/api/inventory', { method: 'GET' });
    }

    // ===== USER API =====

    /**
     * Get user profile
     */
    async getProfile() {
        return this.request('/api/profile', { method: 'GET' });
    }

    // ===== AUTH API =====

    /**
     * Logout user
     */
    async logout() {
        return this.request('/logout', { method: 'GET' });
    }
}

// Create global API instance
const api = new API();
