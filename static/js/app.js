/**
 * Main Application Logic
 */

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", initializeApp);

/**
 * Initialize the application
 */
async function initializeApp() {
  try {
    // Load state from server
    const initialized = await state.initialize();

    if (!initialized) {
      UI.showAlert("Failed to load app data", "error");
      return;
    }

    // Render initial UI
    UI.updateHeader(state.user);
    UI.renderTasks(state.getFilteredTasks());
    UI.renderInventory(state.inventory);
    UI.renderStatistics(state.tasks, state.inventory);

    console.log("✓ App initialized successfully");
  } catch (error) {
    console.error("Failed to initialize app:", error);
    UI.showAlert("An error occurred. Please refresh the page.", "error");
  }
}

/**
 * Add a new task
 */
async function addTask() {
  const title = document.getElementById("taskTitle").value.trim();
  const description = document.getElementById("taskDescription").value.trim();
  const difficulty = document.getElementById("taskDifficulty").value;
  const category = document.getElementById("taskCategory").value;
  const button = event.target;

  if (!title) {
    UI.showAlert("Please enter a quest title", "error");
    return;
  }

  try {
    UI.setLoading(button, true);

    const newTask = await api.createTask(
      title,
      description,
      difficulty,
      category,
    );
    state.addTask(newTask);

    // Clear form
    UI.clearTaskForm();

    // Re-render
    UI.renderTasks(state.getFilteredTasks());
    UI.renderStatistics(state.tasks, state.inventory);
    UI.showAlert("✓ Quest created!", "success");
  } catch (error) {
    console.error("Failed to create task:", error);
    UI.showAlert("Failed to create quest. Please try again.", "error");
  } finally {
    UI.setLoading(button, false);
  }
}

/**
 * Complete a task
 */
async function completeTask(taskId) {
  const button = event.target;
  const taskCard = button.closest(".task-card");

  try {
    button.disabled = true;
    button.textContent = "Completing...";

    // Add completion animation
    taskCard.classList.add("completing");

    const response = await api.completeTask(taskId);

    // Update local state
    state.updateTask(taskId, { completed: true });
    state.updateUserStats({
      total_points: response.user.total_points,
      level: response.user.level,
    });

    // Add loot to inventory
    state.addLootToInventory(response.reward.loot);

    // Animate task completion
    setTimeout(() => {
      taskCard.classList.add("completed");
      taskCard.classList.remove("completing");

      // Update UI after animation
      setTimeout(() => {
        UI.updateHeader(state.user);
        UI.renderTasks(state.getFilteredTasks());
        UI.renderInventory(state.inventory);
        UI.renderStatistics(state.tasks, state.inventory);

        // Show reward popup
        UI.showReward(response.reward.loot, response.reward.points);
      }, 500);
    }, 1000);

    console.log(`✓ Quest completed! +${response.reward.points} points`);
  } catch (error) {
    console.error("Failed to complete task:", error);
    UI.showAlert("Failed to complete quest. Please try again.", "error");

    // Reset button state
    button.disabled = false;
    button.textContent = "Complete";
    taskCard.classList.remove("completing");
  }
}

/**
 * Delete a task
 */
async function deleteTask(taskId) {
  if (!confirm("Are you sure you want to delete this quest?")) {
    return;
  }

  try {
    await api.deleteTask(taskId);
    state.removeTask(taskId);

    // Re-render
    UI.renderTasks(state.getFilteredTasks());
    UI.renderStatistics(state.tasks, state.inventory);
    UI.showAlert("✓ Quest deleted", "success");
  } catch (error) {
    console.error("Failed to delete task:", error);
    UI.showAlert("Failed to delete quest. Please try again.", "error");
  }
}

/**
 * Filter tasks by completion status
 */
function filterTasks(filterType) {
  state.taskFilter = filterType;
  UI.setActiveTab(filterType);
  UI.renderTasks(state.getFilteredTasks());
}

/**
 * Close reward popup
 */
function closeReward() {
  UI.hideReward();
}

/**
 * Logout user
 */
async function logout() {
  if (!confirm("Are you sure you want to logout?")) {
    return;
  }

  try {
    await api.logout();
    window.location.href = "/login";
  } catch (error) {
    console.error("Logout error:", error);
    // Force redirect anyway
    window.location.href = "/login";
  }
}

// Add Enter key support for task creation
document.addEventListener("DOMContentLoaded", () => {
  const taskInput = document.getElementById("taskTitle");
  if (taskInput) {
    taskInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        addTask();
      }
    });
  }
});
