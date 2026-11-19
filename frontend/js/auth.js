/**
 * Authentication Module
 * Handles user login/logout and token management
 */

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:3001'
    : window.location.origin.replace(/\/$/, '');

class AuthManager {
    constructor() {
        this.tokenKey = 'adr_scanner_token';
        this.userKey = 'adr_scanner_user';
        this.loginModal = document.getElementById('loginModal');
        this.loginForm = document.getElementById('loginForm');
        this.logoutBtn = document.getElementById('logoutBtn');
        this.userInfo = document.getElementById('userInfo');
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthentication();
    }

    setupEventListeners() {
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        this.logoutBtn.addEventListener('click', () => this.handleLogout());
    }

    checkAuthentication() {
        const token = localStorage.getItem(this.tokenKey);
        const user = localStorage.getItem(this.userKey);
        
        if (token && user) {
            this.showDashboard(JSON.parse(user));
        } else {
            this.showLoginForm();
        }
    }

    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;
        
        try {
            this.showLoading(true);
            
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email,
                    password,
                    remember_me: rememberMe
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                this.showToast(error.error || 'Login failed', 'error');
                return;
            }
            
            const data = await response.json();
            
            // Store tokens
            localStorage.setItem(this.tokenKey, data.id_token);
            localStorage.setItem(this.userKey, JSON.stringify({
                id: data.user_id,
                email: data.email
            }));
            
            this.showToast('Login successful!', 'success');
            this.showDashboard(JSON.parse(localStorage.getItem(this.userKey)));
            
        } catch (error) {
            console.error('Login error:', error);
            this.showToast('An error occurred during login', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    handleLogout() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
        this.showToast('Logged out successfully', 'info');
        this.showLoginForm();
    }

    showLoginForm() {
        this.loginModal.classList.remove('hidden');
        document.querySelector('.main-content').style.display = 'none';
        this.loginForm.reset();
    }

    showDashboard(user) {
        this.loginModal.classList.add('hidden');
        document.querySelector('.main-content').style.display = 'flex';
        this.userInfo.textContent = user.email || 'User';
    }

    getAuthHeaders() {
        const token = localStorage.getItem(this.tokenKey);
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    isAuthenticated() {
        return !!localStorage.getItem(this.tokenKey);
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (show) {
            spinner.classList.remove('hidden');
        } else {
            spinner.classList.add('hidden');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize auth manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});
