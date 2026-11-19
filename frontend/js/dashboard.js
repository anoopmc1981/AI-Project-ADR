/**
 * Dashboard Module
 * Handles displaying and refreshing scan results
 */

class Dashboard {
    constructor() {
        this.apiBase = API_BASE_URL;
        this.refreshInterval = null;
        this.autoRefreshEnabled = true;
        this.refreshRate = 30000; // 30 seconds
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCrossings();
        this.startAutoRefresh();
        this.checkMarketHours();
    }

    setupEventListeners() {
        document.getElementById('refreshBtn').addEventListener('click', () => this.loadCrossings());
        document.getElementById('applyFiltersBtn').addEventListener('click', () => this.applyFilters());
        document.getElementById('resetFiltersBtn').addEventListener('click', () => this.resetFilters());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportToCSV());
        document.getElementById('autoRefreshToggle').addEventListener('change', (e) => {
            this.autoRefreshEnabled = e.target.checked;
            if (this.autoRefreshEnabled) {
                this.startAutoRefresh();
            } else {
                this.stopAutoRefresh();
            }
        });
    }

    async loadCrossings() {
        try {
            authManager.showLoading(true);
            
            const headers = authManager.getAuthHeaders();
            const response = await fetch(`${this.apiBase}/api/crossings`, {
                method: 'GET',
                headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.displayCrossings(data);
            this.updateLastRefreshTime();
            
        } catch (error) {
            console.error('Error loading crossings:', error);
            authManager.showToast('Failed to load crossings', 'error');
        } finally {
            authManager.showLoading(false);
        }
    }

    displayCrossings(data) {
        const summary = data.summary || {};
        
        // Update summary cards
        document.getElementById('upperCount').textContent = summary.upper_count || 0;
        document.getElementById('lowerCount').textContent = summary.lower_count || 0;
        document.getElementById('totalCount').textContent = summary.total_count || 0;
        
        // Display upper crossings
        const upperBody = document.getElementById('upperBody');
        upperBody.innerHTML = '';
        
        if (data.upper_crossings && data.upper_crossings.length > 0) {
            data.upper_crossings.forEach(crossing => {
                upperBody.appendChild(this.createCrossingRow(crossing));
            });
        } else {
            upperBody.innerHTML = '<tr class="empty-row"><td colspan="9">No upper crossings detected today</td></tr>';
        }
        
        // Display lower crossings
        const lowerBody = document.getElementById('lowerBody');
        lowerBody.innerHTML = '';
        
        if (data.lower_crossings && data.lower_crossings.length > 0) {
            data.lower_crossings.forEach(crossing => {
                lowerBody.appendChild(this.createCrossingRow(crossing));
            });
        } else {
            lowerBody.innerHTML = '<tr class="empty-row"><td colspan="9">No lower crossings detected today</td></tr>';
        }
    }

    createCrossingRow(crossing) {
        const tr = document.createElement('tr');
        
        const timeStr = new Date(crossing.crossing_time).toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        const moveClass = crossing.percentage_move >= 0 ? 'positive' : 'negative';
        const statusBadgeClass = crossing.status === 'ACTIVE' ? 'active' : 'reverted';
        
        tr.innerHTML = `
            <td class="symbol-cell">${crossing.symbol}</td>
            <td class="price-cell">₹${crossing.ltp.toFixed(2)}</td>
            <td class="price-cell">₹${crossing.anchor.toFixed(2)}</td>
            <td class="price-cell">₹${crossing.level.toFixed(2)}</td>
            <td>${crossing.adr_pct.toFixed(2)}%</td>
            <td class="percentage-cell ${moveClass}">
                ${crossing.percentage_move >= 0 ? '↑' : '↓'} ${Math.abs(crossing.percentage_move).toFixed(2)}%
            </td>
            <td>${crossing.volume_vs_avg.toFixed(2)}x</td>
            <td>${timeStr}</td>
            <td>
                <span class="status-badge ${statusBadgeClass}">
                    ${crossing.status === 'ACTIVE' ? 'Active' : 'Reverted'}
                </span>
            </td>
        `;
        
        return tr;
    }

    applyFilters() {
        const direction = document.getElementById('directionFilter').value;
        const minPrice = parseFloat(document.getElementById('minPrice').value) || 0;
        const minVolume = parseFloat(document.getElementById('minVolume').value) || 0;
        const minADR = parseFloat(document.getElementById('minADR').value) || 0;
        const maxADR = parseFloat(document.getElementById('maxADR').value) || 100;
        
        const queryParams = new URLSearchParams();
        queryParams.append('direction', direction);
        if (minPrice > 0) queryParams.append('min_price', minPrice);
        if (minVolume > 0) queryParams.append('min_volume_ratio', minVolume);
        if (minADR > 0) queryParams.append('adr_pct_min', minADR);
        if (maxADR < 100) queryParams.append('adr_pct_max', maxADR);
        
        this.loadCrossingsWithFilters(queryParams.toString());
    }

    async loadCrossingsWithFilters(queryString) {
        try {
            authManager.showLoading(true);
            
            const headers = authManager.getAuthHeaders();
            const response = await fetch(`${this.apiBase}/api/crossings?${queryString}`, {
                method: 'GET',
                headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.displayCrossings(data);
            authManager.showToast('Filters applied', 'info');
            
        } catch (error) {
            console.error('Error applying filters:', error);
            authManager.showToast('Failed to apply filters', 'error');
        } finally {
            authManager.showLoading(false);
        }
    }

    resetFilters() {
        document.getElementById('directionFilter').value = 'both';
        document.getElementById('minPrice').value = '';
        document.getElementById('minVolume').value = '';
        document.getElementById('minADR').value = '';
        document.getElementById('maxADR').value = '';
        this.loadCrossings();
    }

    exportToCSV() {
        const upperBody = document.getElementById('upperBody');
        const lowerBody = document.getElementById('lowerBody');
        
        let csv = 'Type,Symbol,LTP,Anchor,Level,ADR %,% Move,Vol/Avg,Time,Status\n';
        
        // Extract upper crossings
        upperBody.querySelectorAll('tr:not(.empty-row)').forEach(row => {
            const cells = row.querySelectorAll('td');
            const rowData = Array.from(cells).map(cell => {
                let text = cell.textContent.trim();
                if (text.includes(',') || text.includes('"')) {
                    text = `"${text.replace(/"/g, '""')}"`;
                }
                return text;
            });
            csv += `Upper,${rowData.join(',')}\n`;
        });
        
        // Extract lower crossings
        lowerBody.querySelectorAll('tr:not(.empty-row)').forEach(row => {
            const cells = row.querySelectorAll('td');
            const rowData = Array.from(cells).map(cell => {
                let text = cell.textContent.trim();
                if (text.includes(',') || text.includes('"')) {
                    text = `"${text.replace(/"/g, '""')}"`;
                }
                return text;
            });
            csv += `Lower,${rowData.join(',')}\n`;
        });
        
        // Download CSV
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `adr-crossings-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        authManager.showToast('CSV exported successfully', 'success');
    }

    updateLastRefreshTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('lastUpdate').textContent = timeStr;
    }

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            if (this.autoRefreshEnabled) {
                this.loadCrossings();
            }
        }, this.refreshRate);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    checkMarketHours() {
        // NSE market hours: 9:15 AM to 3:30 PM IST (Monday to Friday)
        const now = new Date();
        const istHours = now.getHours() + 5; // UTC to IST offset
        const istMinutes = now.getMinutes() + 30;
        
        const dayOfWeek = now.getDay();
        const isWeekday = dayOfWeek >= 1 && dayOfWeek <= 5;
        const isMarketOpen = isWeekday && (
            (istHours > 9 && istHours < 15) ||
            (istHours === 9 && istMinutes >= 15) ||
            (istHours === 15 && istMinutes <= 30)
        );
        
        const statusText = document.getElementById('marketStatusText');
        if (isMarketOpen) {
            statusText.textContent = '🟢 Market Status: OPEN';
            statusText.style.color = 'var(--upper-color)';
        } else {
            statusText.textContent = '🔴 Market Status: CLOSED';
            statusText.style.color = 'var(--lower-color)';
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for auth manager to initialize
    setTimeout(() => {
        if (authManager.isAuthenticated()) {
            window.dashboard = new Dashboard();
        }
    }, 100);
});
