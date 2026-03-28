/**
 * State Module - Client-side state management
 */

class AppState {
    constructor() {
        this.user = null;
        this.tasks = [];
        this.inventory = [];
        this.taskFilter = 'all'; // 'all', 'active', 'completed'
        this.isLoading = false;
    }

    /**
     * Initialize app state from server
     */
    async initialize() {
        try {
            this.isLoading = true;
            
            // Fetch user profile
            const userProfile = await api.getProfile();
            this.user = userProfile;
            
            // Fetch tasks
            this.tasks = await api.getTasks();
            
            // Fetch inventory
            this.inventory = await api.getInventory();
            
            this.isLoading = false;
            return true;
        } catch (error) {
            console.error('Failed to initialize app state:', error);
            this.isLoading = false;
            return false;
        }
    }

    /**
     * Add a new task to state
     */
    addTask(task) {
        this.tasks.push(task);
    }

    /**
     * Update task in state
     */
    updateTask(taskId, updates) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            Object.assign(task, updates);
        }
    }

    /**
     * Remove task from state
     */
    removeTask(taskId) {
        this.tasks = this.tasks.filter(t => t.id !== taskId);
    }

    /**
     * Get filtered tasks
     */
    getFilteredTasks() {
        switch (this.taskFilter) {
            case 'active':
                return this.tasks.filter(t => !t.completed);
            case 'completed':
                return this.tasks.filter(t => t.completed);
            default:
                return this.tasks;
        }
    }

    /**
     * Add loot item to inventory
     */
    addLootToInventory(lootItem) {
        // Check if item already exists
        const existing = this.inventory.find(inv => inv.loot_item.id === lootItem.id);
        if (existing) {
            existing.quantity += 1;
        } else {
            this.inventory.push({
                id: Date.now(), // Temporary ID
                loot_item: lootItem,
                quantity: 1,
                acquired_at: new Date().toISOString()
            });
        }
    }

    /**
     * Update user stats
     */
    updateUserStats(newStats) {
        if (this.user) {
            Object.assign(this.user, newStats);
        }
    }
}

// Create global state instance
const state = new AppState();
