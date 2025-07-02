class Dashboard {
    constructor() {
        this.tasks = [];
        this.completedTasks = 0;
        this.hoursWorked = 0;
        this.activeProjects = 3;
        this.init();
    }

    init() {
        this.updateCurrentTime();
        this.updateStats();
        this.bindEvents();
        this.loadSampleTasks();
        
        // Update time every second
        setInterval(() => this.updateCurrentTime(), 1000);
        
        // Simulate work progress
        this.simulateProgress();
    }

    updateCurrentTime() {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        
        const timeString = now.toLocaleDateString('en-US', options);
        document.getElementById('current-time').textContent = timeString;
    }

    updateStats() {
        this.animateNumber('completed-tasks', this.completedTasks);
        this.animateNumber('hours-worked', this.hoursWorked);
        this.animateNumber('active-projects', this.activeProjects);
    }

    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        const currentValue = parseInt(element.textContent) || 0;
        const increment = targetValue > currentValue ? 1 : -1;
        const step = Math.abs(targetValue - currentValue) / 20;

        let current = currentValue;
        const timer = setInterval(() => {
            current += increment * step;
            if ((increment > 0 && current >= targetValue) || 
                (increment < 0 && current <= targetValue)) {
                current = targetValue;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 50);
    }

    bindEvents() {
        const addTaskBtn = document.getElementById('add-task-btn');
        const newTaskInput = document.getElementById('new-task');

        addTaskBtn.addEventListener('click', () => this.addTask());
        
        newTaskInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addTask();
            }
        });

        // Smooth scrolling for navigation
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.scrollIntoView({ 
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    addTask() {
        const input = document.getElementById('new-task');
        const taskText = input.value.trim();
        
        if (!taskText) {
            this.showNotification('Please enter a task!', 'error');
            return;
        }

        const task = {
            id: Date.now(),
            text: taskText,
            completed: false,
            createdAt: new Date()
        };

        this.tasks.push(task);
        this.renderTask(task);
        input.value = '';
        this.showNotification('Task added successfully!', 'success');
    }

    renderTask(task) {
        const taskList = document.getElementById('task-list');
        const taskItem = document.createElement('li');
        taskItem.className = `task-item ${task.completed ? 'completed' : ''}`;
        taskItem.dataset.taskId = task.id;

        taskItem.innerHTML = `
            <span class="task-text">${task.text}</span>
            <div class="task-actions">
                <button class="btn-small btn-complete" onclick="dashboard.toggleTask(${task.id})">
                    ${task.completed ? 'Undo' : 'Complete'}
                </button>
                <button class="btn-small btn-delete" onclick="dashboard.deleteTask(${task.id})">
                    Delete
                </button>
            </div>
        `;

        taskList.appendChild(taskItem);
    }

    toggleTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;

        task.completed = !task.completed;
        
        if (task.completed) {
            this.completedTasks++;
            this.showNotification('Task completed! 🎉', 'success');
        } else {
            this.completedTasks--;
        }

        this.updateStats();
        this.updateTaskDisplay(taskId);
    }

    deleteTask(taskId) {
        const taskIndex = this.tasks.findIndex(t => t.id === taskId);
        if (taskIndex === -1) return;

        const task = this.tasks[taskIndex];
        if (task.completed) {
            this.completedTasks--;
        }

        this.tasks.splice(taskIndex, 1);
        this.updateStats();
        
        const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
        if (taskElement) {
            taskElement.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => taskElement.remove(), 300);
        }
        
        this.showNotification('Task deleted', 'info');
    }

    updateTaskDisplay(taskId) {
        const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
        const task = this.tasks.find(t => t.id === taskId);
        
        if (taskElement && task) {
            taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;
            const completeBtn = taskElement.querySelector('.btn-complete');
            completeBtn.textContent = task.completed ? 'Undo' : 'Complete';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '600',
            zIndex: '1000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            backgroundColor: type === 'success' ? '#10b981' : 
                           type === 'error' ? '#ef4444' : '#6366f1'
        });

        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Animate out and remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    loadSampleTasks() {
        const sampleTasks = [
            'Review project proposal',
            'Update team documentation',
            'Prepare for client meeting'
        ];

        sampleTasks.forEach(taskText => {
            const task = {
                id: Date.now() + Math.random(),
                text: taskText,
                completed: false,
                createdAt: new Date()
            };
            this.tasks.push(task);
            this.renderTask(task);
        });
    }

    simulateProgress() {
        setInterval(() => {
            if (Math.random() > 0.7) { // 30% chance every 10 seconds
                this.hoursWorked += 0.1;
                this.updateStats();
            }
        }, 10000);
    }
}

// Initialize dashboard when page loads
const dashboard = new Dashboard();

// Add slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(-20px); }
    }
`;
document.head.appendChild(style);