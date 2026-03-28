/**
 * UI Module - Handles all DOM manipulation and rendering
 */

class UI {
  /**
   * Update user header info
   */
  static updateHeader(user) {
    document.getElementById("username").textContent = user.username || "Player";
    document.getElementById("userLevel").textContent = user.level || 1;
    document.getElementById("userPoints").textContent = user.total_points || 0;
  }

  /**
   * Render all tasks
   */
  static renderTasks(tasks) {
    const container = document.getElementById("tasksList");

    if (tasks.length === 0) {
      container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-emoji">🗺️</div>
                    <div class="empty-state-text">No quests yet!</div>
                    <p>Create your first quest to begin your adventure.</p>
                </div>
            `;
      return;
    }

    container.innerHTML = tasks
      .map((task) => this.createTaskCard(task))
      .join("");
  }

  /**
   * Create a single task card HTML
   */
  static createTaskCard(task) {
    const difficultyClass = `difficulty-${task.difficulty}`;
    const categoryClass = `category-${task.category}`;
    const completedClass = task.completed ? " completed" : "";
    const checkmark = task.completed ? "✅" : "📝";

    return `
            <div class="task-card${completedClass}">
                <div class="task-info">
                    <div class="task-title">${checkmark} ${this.escapeHTML(task.title)}</div>
                    <div class="task-meta">
                        <span class="category-badge ${categoryClass}">${task.category}</span>
                        <span class="difficulty-badge ${difficultyClass}">
                            ${task.difficulty}
                        </span>
                        <span>+${task.reward_points} points</span>
                    </div>
                </div>
                <div class="task-actions">
                    ${
                      !task.completed
                        ? `
                        <button class="btn btn-primary" onclick="completeTask(${task.id})">
                            Complete
                        </button>
                    `
                        : ""
                    }
                    <button class="btn btn-danger" onclick="deleteTask(${task.id})">
                        Delete
                    </button>
                </div>
            </div>
        `;
  }

  /**
   * Render inventory grid
   */
  static renderInventory(inventoryItems) {
    const container = document.getElementById("inventoryGrid");

    if (inventoryItems.length === 0) {
      container.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <div class="empty-state-emoji">🎁</div>
                    <div class="empty-state-text">Empty Inventory</div>
                    <p>Complete quests to collect loot!</p>
                </div>
            `;
      return;
    }

    container.innerHTML = inventoryItems
      .map((item) => this.createLootCard(item))
      .join("");
  }

  /**
   * Render user statistics
   */
  static renderStatistics(tasks, inventory) {
    // Calculate stats
    const completedTasks = tasks.filter((t) => t.completed);
    const totalCompleted = completedTasks.length;
    const totalLoot = inventory.reduce((sum, item) => sum + item.quantity, 0);

    // Average difficulty of completed tasks
    const avgDifficulty =
      completedTasks.length > 0
        ? (
            completedTasks.reduce(
              (sum, task) => sum + this.getDifficultyValue(task.difficulty),
              0,
            ) / completedTasks.length
          ).toFixed(1)
        : 0;

    // Days active (simplified - just count unique days from task creation)
    const uniqueDays = new Set(
      tasks.map((t) => new Date(t.created_at).toDateString()),
    ).size;

    // Update DOM
    document.getElementById("totalCompleted").textContent = totalCompleted;
    document.getElementById("totalLoot").textContent = totalLoot;
    document.getElementById("avgDifficulty").textContent = avgDifficulty;
    document.getElementById("daysActive").textContent = uniqueDays;
  }

  /**
   * Get numeric value for difficulty
   */
  static getDifficultyValue(difficulty) {
    const values = { easy: 1, medium: 2, hard: 3, legendary: 4 };
    return values[difficulty] || 2;
  }

  /**
   * Create a single loot card HTML
   */
  static createLootCard(inventoryItem) {
    const item = inventoryItem.loot_item;
    const rarityClass = `rarity-${item.rarity}`;

    return `
            <div class="loot-item">
                <div class="loot-rarity-badge ${rarityClass}">
                    ${item.rarity}
                </div>
                <div class="loot-emoji">${item.emoji}</div>
                <div class="loot-name">${this.escapeHTML(item.name)}</div>
                <div class="loot-quantity">${inventoryItem.quantity}</div>
            </div>
        `;
  }

  /**
   * Show reward popup
   */
  static showReward(lootItem, points) {
    const popup = document.getElementById("rewardPopup");
    const overlay = document.getElementById("rewardOverlay");

    document.getElementById("rewardEmoji").textContent = lootItem.emoji;
    document.getElementById("rewardName").textContent = lootItem.name;
    document.getElementById("rewardPoints").textContent = `+${points} points`;
    document.getElementById("rewardRarity").textContent =
      lootItem.rarity.toUpperCase();

    // Add rarity color class
    const rarityElement = document.getElementById("rewardRarity");
    rarityElement.className = `rarity-${lootItem.rarity}`;

    popup.classList.add("show");
    overlay.classList.add("show");

    // Auto-hide after 3 seconds
    setTimeout(() => {
      this.hideReward();
    }, 3000);
  }

  /**
   * Hide reward popup
   */
  static hideReward() {
    document.getElementById("rewardPopup").classList.remove("show");
    document.getElementById("rewardOverlay").classList.remove("show");
  }

  /**
   * Show notification/alert
   */
  static showAlert(message, type = "info") {
    // Create temp alert element
    const alert = document.createElement("div");
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    // Insert at top of main
    const main = document.querySelector("main");
    main.insertBefore(alert, main.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      alert.remove();
    }, 5000);
  }

  /**
   * Clear all input fields
   */
  static clearTaskForm() {
    document.getElementById("taskTitle").value = "";
    document.getElementById("taskDescription").value = "";
    document.getElementById("taskDifficulty").value = "medium";
    document.getElementById("taskCategory").value = "general";
  }

  /**
   * Set loading state
   */
  static setLoading(button, isLoading) {
    if (isLoading) {
      button.disabled = true;
      button.innerHTML = '<span class="loading-spinner"></span>';
    } else {
      button.disabled = false;
      button.innerHTML = "+ Create Quest";
    }
  }

  /**
   * Utility: Escape HTML special characters
   */
  static escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Update tab button active state
   */
  static setActiveTab(filterType) {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    event.target.classList.add("active");
  }
}
