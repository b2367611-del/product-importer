// Product Importer Frontend Application
class ProductImporter {
    constructor() {
        this.currentTab = 'upload';
        this.currentPage = 1;
        this.pageSize = 50;
        this.currentTaskId = null;
        this.progressInterval = null;
        this.jobsRefreshInterval = null;
        this.webhooks = []; // Store webhooks for testing
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
    }
    
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('[data-tab]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // File upload
        document.getElementById('upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFileUpload();
        });
        
        // Product management
        document.getElementById('add-product-btn').addEventListener('click', () => {
            this.showProductModal();
        });
        
        document.getElementById('delete-all-btn').addEventListener('click', () => {
            this.deleteAllProducts();
        });
        
        document.getElementById('product-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProduct();
        });
        
        // Product filters
        document.getElementById('filter-btn').addEventListener('click', () => {
            this.currentPage = 1;
            this.loadProducts();
        });
        
        document.getElementById('clear-filters-btn').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Webhook management
        document.getElementById('add-webhook-btn').addEventListener('click', () => {
            this.showWebhookModal();
        });
        
        document.getElementById('webhook-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveWebhook();
        });
    }
    
    switchTab(tabName) {
        // Stop any existing jobs refresh interval
        this.stopJobsAutoRefresh();
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Show/hide content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-section`).classList.add('active');
        
        this.currentTab = tabName;
        
        // Load data for the selected tab
        switch (tabName) {
            case 'products':
                this.loadProducts();
                break;
            case 'webhooks':
                this.loadWebhooks();
                break;
            case 'jobs':
                this.loadImportJobs();
                this.startJobsAutoRefresh(); // Start auto-refresh for jobs
                break;
        }
    }
    
    loadInitialData() {
        // Load data for the default tab
        this.switchTab('upload');
    }
    
    async handleFileUpload() {
        const fileInput = document.getElementById('csvFile');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showToast('Please select a file', 'error');
            return;
        }
        
        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showToast('Please select a CSV file', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadBtn = document.getElementById('upload-btn');
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<div class="loading-spinner"></div> Uploading...';
        
        try {
            const response = await fetch('/api/v1/import/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }
            
            const result = await response.json();
            this.currentTaskId = result.task_id;
            
            // Show progress section
            document.getElementById('progress-section').style.display = 'block';
            
            // Start progress tracking
            this.startProgressTracking();
            
            // Reset form
            fileInput.value = '';
            
            this.showToast('File uploaded successfully! Processing...', 'success');
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast(error.message, 'error');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="bi bi-upload"></i> Upload File';
        }
    }
    
    startProgressTracking() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/v1/import/progress/${this.currentTaskId}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch progress');
                }
                
                const progress = await response.json();
                this.updateProgressUI(progress);
                
                // Stop tracking if completed or failed
                if (progress.status === 'completed' || progress.status === 'failed') {
                    clearInterval(this.progressInterval);
                    this.progressInterval = null;
                    
                    if (progress.status === 'completed') {
                        this.showToast('Import completed successfully!', 'success');
                    } else {
                        this.showToast('Import failed: ' + (progress.error_message || 'Unknown error'), 'error');
                    }
                }
                
            } catch (error) {
                console.error('Progress tracking error:', error);
            }
        }, 2000); // Update every 2 seconds
    }
    
    startJobsAutoRefresh() {
        // Show auto-refresh indicator
        const indicator = document.getElementById('jobs-auto-refresh');
        if (indicator) {
            indicator.style.display = 'inline';
        }
        
        // Refresh jobs every 5 seconds when on the jobs tab
        this.jobsRefreshInterval = setInterval(() => {
            if (this.currentTab === 'jobs') {
                this.loadImportJobs();
            }
        }, 5000); // Update every 5 seconds
    }
    
    stopJobsAutoRefresh() {
        // Hide auto-refresh indicator
        const indicator = document.getElementById('jobs-auto-refresh');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        if (this.jobsRefreshInterval) {
            clearInterval(this.jobsRefreshInterval);
            this.jobsRefreshInterval = null;
        }
    }
    
    updateProgressUI(progress) {
        const progressBar = document.getElementById('progress-bar');
        const statusText = document.getElementById('status-text');
        const processedCount = document.getElementById('processed-count');
        const totalCount = document.getElementById('total-count');
        const successfulCount = document.getElementById('successful-count');
        const failedCount = document.getElementById('failed-count');
        const etaText = document.getElementById('eta-text');
        
        // Update progress bar
        progressBar.style.width = `${progress.progress_percentage}%`;
        progressBar.textContent = `${progress.progress_percentage}%`;
        
        // Update status
        statusText.textContent = progress.status.charAt(0).toUpperCase() + progress.status.slice(1);
        statusText.className = `badge bg-${this.getStatusColor(progress.status)}`;
        
        // Update counts
        processedCount.textContent = progress.processed_records.toLocaleString();
        totalCount.textContent = progress.total_records.toLocaleString();
        successfulCount.textContent = progress.successful_records.toLocaleString();
        failedCount.textContent = progress.failed_records.toLocaleString();
        
        // Update ETA
        if (progress.estimated_time_remaining) {
            etaText.textContent = this.formatDuration(progress.estimated_time_remaining);
        } else {
            etaText.textContent = progress.status === 'completed' ? 'Completed' : 'Calculating...';
        }
    }
    
    getStatusColor(status) {
        switch (status) {
            case 'pending': return 'secondary';
            case 'processing': return 'primary';
            case 'completed': return 'success';
            case 'failed': return 'danger';
            default: return 'secondary';
        }
    }
    
    formatDuration(seconds) {
        if (seconds < 60) {
            return `${seconds}s`;
        } else if (seconds < 3600) {
            return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
        } else {
            return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
        }
    }
    
    async loadProducts() {
        const filters = this.getProductFilters();
        const queryParams = new URLSearchParams({
            page: this.currentPage,
            size: this.pageSize,
            ...filters
        });
        
        try {
            const response = await fetch(`/api/v1/products?${queryParams}`);
            if (!response.ok) {
                throw new Error('Failed to load products');
            }
            
            const data = await response.json();
            this.renderProducts(data.items);
            this.renderPagination(data);
            
        } catch (error) {
            console.error('Load products error:', error);
            this.showToast('Failed to load products', 'error');
        }
    }
    
    getProductFilters() {
        const filters = {};
        
        const sku = document.getElementById('filter-sku').value.trim();
        if (sku) filters.sku = sku;
        
        const name = document.getElementById('filter-name').value.trim();
        if (name) filters.name = name;
        
        const isActive = document.getElementById('filter-active').value;
        if (isActive !== '') filters.is_active = isActive === 'true';
        
        return filters;
    }
    
    clearFilters() {
        document.getElementById('filter-sku').value = '';
        document.getElementById('filter-name').value = '';
        document.getElementById('filter-active').value = '';
        this.currentPage = 1;
        this.loadProducts();
    }
    
    renderProducts(products) {
        const tbody = document.getElementById('products-tbody');
        
        if (products.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No products found</td></tr>';
            return;
        }
        
        tbody.innerHTML = products.map(product => `
            <tr>
                <td><code>${this.escapeHtml(product.sku)}</code></td>
                <td class="text-truncate" title="${this.escapeHtml(product.name)}">
                    ${this.escapeHtml(product.name)}
                </td>
                <td>
                    ${product.price ? `$${product.price.toFixed(2)}` : '-'}
                </td>
                <td>${this.escapeHtml(product.category || '-')}</td>
                <td>
                    <span class="badge bg-${product.is_active ? 'success' : 'secondary'}">
                        ${product.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="app.editProduct(${product.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="app.deleteProduct(${product.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    renderPagination(data) {
        const pagination = document.getElementById('products-pagination');
        
        if (data.pages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // Previous button
        if (data.page > 1) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="app.goToPage(${data.page - 1})">Previous</a>
            </li>`;
        }
        
        // Page numbers
        const start = Math.max(1, data.page - 2);
        const end = Math.min(data.pages, data.page + 2);
        
        for (let i = start; i <= end; i++) {
            html += `<li class="page-item ${i === data.page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="app.goToPage(${i})">${i}</a>
            </li>`;
        }
        
        // Next button
        if (data.page < data.pages) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="app.goToPage(${data.page + 1})">Next</a>
            </li>`;
        }
        
        pagination.innerHTML = html;
    }
    
    goToPage(page) {
        this.currentPage = page;
        this.loadProducts();
    }
    
    showProductModal(product = null) {
        const modal = new bootstrap.Modal(document.getElementById('productModal'));
        const form = document.getElementById('product-form');
        const title = document.getElementById('productModalTitle');
        
        // Reset form
        form.reset();
        
        if (product) {
            title.textContent = 'Edit Product';
            document.getElementById('product-id').value = product.id;
            document.getElementById('product-sku').value = product.sku;
            document.getElementById('product-name').value = product.name;
            document.getElementById('product-description').value = product.description || '';
            document.getElementById('product-price').value = product.price || '';
            document.getElementById('product-inventory').value = product.inventory_count || 0;
            document.getElementById('product-category').value = product.category || '';
            document.getElementById('product-brand').value = product.brand || '';
            document.getElementById('product-active').checked = product.is_active;
        } else {
            title.textContent = 'Add Product';
            document.getElementById('product-id').value = '';
            document.getElementById('product-active').checked = true;
        }
        
        modal.show();
    }
    
    async saveProduct() {
        const productId = document.getElementById('product-id').value;
        const isEdit = Boolean(productId);
        
        const productData = {
            sku: document.getElementById('product-sku').value.trim(),
            name: document.getElementById('product-name').value.trim(),
            description: document.getElementById('product-description').value.trim() || null,
            price: parseFloat(document.getElementById('product-price').value) || null,
            inventory_count: parseInt(document.getElementById('product-inventory').value) || 0,
            category: document.getElementById('product-category').value.trim() || null,
            brand: document.getElementById('product-brand').value.trim() || null,
            is_active: document.getElementById('product-active').checked
        };
        
        try {
            const url = isEdit ? `/api/v1/products/${productId}` : '/api/v1/products/';
            const method = isEdit ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(productData)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to save product');
            }
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('productModal')).hide();
            
            // Reload products
            this.loadProducts();
            
            this.showToast(`Product ${isEdit ? 'updated' : 'created'} successfully!`, 'success');
            
        } catch (error) {
            console.error('Save product error:', error);
            this.showToast(error.message, 'error');
        }
    }
    
    async editProduct(productId) {
        try {
            const response = await fetch(`/api/v1/products/${productId}`);
            if (!response.ok) {
                throw new Error('Failed to load product');
            }
            
            const product = await response.json();
            this.showProductModal(product);
            
        } catch (error) {
            console.error('Edit product error:', error);
            this.showToast('Failed to load product details', 'error');
        }
    }
    
    async deleteProduct(productId) {
        if (!confirm('Are you sure you want to delete this product?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/v1/products/${productId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete product');
            }
            
            this.loadProducts();
            this.showToast('Product deleted successfully!', 'success');
            
        } catch (error) {
            console.error('Delete product error:', error);
            this.showToast('Failed to delete product', 'error');
        }
    }
    
    async deleteAllProducts() {
        const confirmation = prompt(
            'This will delete ALL products permanently. Type "DELETE ALL" to confirm:'
        );
        
        if (confirmation !== 'DELETE ALL') {
            return;
        }
        
        try {
            const response = await fetch('/api/v1/products/?confirm=true', {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete products');
            }
            
            const result = await response.json();
            this.loadProducts();
            this.showToast(result.message, 'success');
            
        } catch (error) {
            console.error('Delete all products error:', error);
            this.showToast('Failed to delete products', 'error');
        }
    }
    
    async loadWebhooks() {
        try {
            const response = await fetch('/api/v1/webhooks/');
            if (!response.ok) {
                throw new Error('Failed to load webhooks');
            }
            
            const webhooks = await response.json();
            this.webhooks = webhooks; // Store webhooks for testing
            this.renderWebhooks(webhooks);
            
        } catch (error) {
            console.error('Load webhooks error:', error);
            this.showToast('Failed to load webhooks', 'error');
        }
    }
    
    renderWebhooks(webhooks) {
        const tbody = document.getElementById('webhooks-tbody');
        
        if (webhooks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No webhooks found</td></tr>';
            return;
        }
        
        tbody.innerHTML = webhooks.map(webhook => `
            <tr>
                <td>${this.escapeHtml(webhook.name)}</td>
                <td class="text-truncate" title="${this.escapeHtml(webhook.url)}">
                    <a href="${this.escapeHtml(webhook.url)}" target="_blank">
                        ${this.escapeHtml(webhook.url)}
                    </a>
                </td>
                <td>
                    <span class="badge bg-info">${webhook.event_types.length} events</span>
                </td>
                <td>
                    <span class="badge bg-${webhook.is_active ? 'success' : 'secondary'}">
                        ${webhook.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    ${webhook.last_response_code ? 
                        `<div>
                            <span class="badge bg-${webhook.last_response_code < 300 ? 'success' : 'danger'}">
                                ${webhook.last_response_code}
                            </span>
                            ${webhook.last_response_time_ms ? 
                                `<br><small class="text-muted">${webhook.last_response_time_ms}ms</small>` : 
                                ''
                            }
                        </div>` : 
                        '<span class="text-muted">Never tested</span>'
                    }
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-info" onclick="app.testWebhook(${webhook.id})">
                            <i class="bi bi-play"></i>
                        </button>
                        <button class="btn btn-outline-primary" onclick="app.editWebhook(${webhook.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="app.deleteWebhook(${webhook.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    showWebhookModal(webhook = null) {
        const modal = new bootstrap.Modal(document.getElementById('webhookModal'));
        const form = document.getElementById('webhook-form');
        const title = document.getElementById('webhookModalTitle');
        
        // Reset form
        form.reset();
        document.querySelectorAll('.event-type').forEach(cb => cb.checked = false);
        
        if (webhook) {
            title.textContent = 'Edit Webhook';
            document.getElementById('webhook-id').value = webhook.id;
            document.getElementById('webhook-name').value = webhook.name;
            document.getElementById('webhook-url').value = webhook.url;
            document.getElementById('webhook-timeout').value = webhook.timeout_seconds;
            document.getElementById('webhook-retries').value = webhook.retry_count;
            document.getElementById('webhook-secret').value = webhook.secret_key || '';
            document.getElementById('webhook-active').checked = webhook.is_active;
            
            // Set event types
            webhook.event_types.forEach(eventType => {
                const checkbox = document.querySelector(`.event-type[value="${eventType}"]`);
                if (checkbox) checkbox.checked = true;
            });
        } else {
            title.textContent = 'Add Webhook';
            document.getElementById('webhook-id').value = '';
            document.getElementById('webhook-timeout').value = 30;
            document.getElementById('webhook-retries').value = 3;
            document.getElementById('webhook-active').checked = true;
        }
        
        modal.show();
    }
    
    async saveWebhook() {
        const webhookId = document.getElementById('webhook-id').value;
        const isEdit = Boolean(webhookId);
        
        // Get selected event types
        const eventTypes = Array.from(document.querySelectorAll('.event-type:checked'))
            .map(cb => cb.value);
        
        if (eventTypes.length === 0) {
            this.showToast('Please select at least one event type', 'error');
            return;
        }
        
        const webhookData = {
            name: document.getElementById('webhook-name').value.trim(),
            url: document.getElementById('webhook-url').value.trim(),
            event_types: eventTypes,
            timeout_seconds: parseInt(document.getElementById('webhook-timeout').value),
            retry_count: parseInt(document.getElementById('webhook-retries').value),
            secret_key: document.getElementById('webhook-secret').value.trim() || null,
            is_active: document.getElementById('webhook-active').checked
        };
        
        try {
            const url = isEdit ? `/api/v1/webhooks/${webhookId}` : '/api/v1/webhooks/';
            const method = isEdit ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(webhookData)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to save webhook');
            }
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('webhookModal')).hide();
            
            // Reload webhooks
            this.loadWebhooks();
            
            this.showToast(`Webhook ${isEdit ? 'updated' : 'created'} successfully!`, 'success');
            
        } catch (error) {
            console.error('Save webhook error:', error);
            this.showToast(error.message, 'error');
        }
    }
    
    async editWebhook(webhookId) {
        try {
            const response = await fetch(`/api/v1/webhooks/${webhookId}`);
            if (!response.ok) {
                throw new Error('Failed to load webhook');
            }
            
            const webhook = await response.json();
            this.showWebhookModal(webhook);
            
        } catch (error) {
            console.error('Edit webhook error:', error);
            this.showToast('Failed to load webhook details', 'error');
        }
    }
    
    async deleteWebhook(webhookId) {
        if (!confirm('Are you sure you want to delete this webhook?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/v1/webhooks/${webhookId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete webhook');
            }
            
            this.loadWebhooks();
            this.showToast('Webhook deleted successfully!', 'success');
            
        } catch (error) {
            console.error('Delete webhook error:', error);
            this.showToast('Failed to delete webhook', 'error');
        }
    }
    
    async testWebhook(webhookId) {
        // Show loading state
        const testButton = document.querySelector(`button[onclick="app.testWebhook(${webhookId})"]`);
        const originalHtml = testButton.innerHTML;
        testButton.innerHTML = '<i class="bi bi-arrow-clockwise fa-spin"></i>';
        testButton.disabled = true;
        
        try {
            // Get the webhook to determine its event type
            const webhook = this.webhooks.find(w => w.id === webhookId);
            if (!webhook || !webhook.event_types || webhook.event_types.length === 0) {
                throw new Error('Webhook not found or has no event types');
            }
            
            // Use the first event type from the webhook
            const eventType = webhook.event_types[0];
            
            // Generate appropriate test data based on event type
            let testData;
            if (eventType === 'product.created') {
                testData = {
                    event_type: eventType,
                    test_data: {
                        id: 123,
                        sku: 'TEST-SKU-CREATED',
                        name: 'Test Product Created',
                        timestamp: new Date().toISOString()
                    }
                };
            } else if (eventType === 'product.updated') {
                testData = {
                    event_type: eventType,
                    test_data: {
                        id: 456,
                        sku: 'TEST-SKU-UPDATED',
                        name: 'Test Product Updated',
                        timestamp: new Date().toISOString()
                    }
                };
            } else if (eventType === 'product.deleted') {
                testData = {
                    event_type: eventType,
                    test_data: {
                        id: 789,
                        sku: 'TEST-SKU-DELETED',
                        name: 'Test Product Deleted',
                        timestamp: new Date().toISOString()
                    }
                };
            } else if (eventType === 'import.completed') {
                testData = {
                    event_type: eventType,
                    test_data: {
                        import_job_id: 999,
                        total_processed: 100,
                        successful_imports: 95,
                        failed_imports: 5,
                        processing_time_seconds: 45.2
                    }
                };
            } else {
                // Fallback for unknown event types
                testData = {
                    event_type: eventType,
                    test_data: {
                        id: 123,
                        timestamp: new Date().toISOString(),
                        message: `Test data for ${eventType}`
                    }
                };
            }
            
            const response = await fetch(`/api/v1/webhooks/${webhookId}/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(testData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to test webhook');
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast(
                    `✅ Webhook test successful! Response: ${result.response_code} (${result.response_time_ms}ms)`, 
                    'success'
                );
                // Show temporary success state
                testButton.innerHTML = '<i class="bi bi-check-circle text-success"></i>';
                testButton.classList.add('btn-success');
                testButton.classList.remove('btn-outline-info');
            } else {
                this.showToast(
                    `❌ Webhook test failed: ${result.error_message || 'Unknown error'}`, 
                    'error'
                );
                // Show temporary error state
                testButton.innerHTML = '<i class="bi bi-x-circle text-danger"></i>';
                testButton.classList.add('btn-danger');
                testButton.classList.remove('btn-outline-info');
            }
            
            // Reload webhooks to show updated response code and time
            setTimeout(() => {
                this.loadWebhooks();
            }, 1000); // Delay to show the success/error state
            
        } catch (error) {
            console.error('Test webhook error:', error);
            this.showToast('Failed to test webhook', 'error');
        } finally {
            // Restore button state after showing result
            setTimeout(() => {
                testButton.innerHTML = originalHtml;
                testButton.disabled = false;
                testButton.classList.remove('btn-success', 'btn-danger');
                testButton.classList.add('btn-outline-info');
            }, 2000); // Show result for 2 seconds
        }
    }
    
    async loadImportJobs() {
        try {
            const response = await fetch('/api/v1/import/jobs');
            if (!response.ok) {
                throw new Error('Failed to load import jobs');
            }
            
            const jobs = await response.json();
            this.renderImportJobs(jobs);
            
        } catch (error) {
            console.error('Load import jobs error:', error);
            this.showToast('Failed to load import jobs', 'error');
        }
    }
    
    renderImportJobs(jobs) {
        const tbody = document.getElementById('jobs-tbody');
        
        if (jobs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No import jobs found</td></tr>';
            return;
        }
        
        // Check if there are any processing jobs for auto-refresh indicator
        const hasProcessingJobs = jobs.some(job => job.status === 'processing' || job.status === 'pending');
        
        tbody.innerHTML = jobs.map(job => {
            const successRate = job.total_records > 0 ? 
                ((job.successful_records / job.total_records) * 100).toFixed(1) : 0;
            
            const duration = job.started_at && job.completed_at ?
                this.formatDuration(
                    Math.floor((new Date(job.completed_at) - new Date(job.started_at)) / 1000)
                ) : (job.status === 'processing' ? 'Running...' : '-');
            
            return `
                <tr>
                    <td class="text-truncate" title="${this.escapeHtml(job.filename)}">
                        ${this.escapeHtml(job.filename)}
                    </td>
                    <td>
                        <span class="badge status-${job.status} ${job.status === 'processing' ? 'badge-pulse' : ''}">
                            ${job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                            ${job.status === 'processing' ? ' <i class="bi bi-arrow-clockwise fa-spin"></i>' : ''}
                        </span>
                    </td>
                    <td>
                        <div class="progress" style="height: 20px; width: 100px;">
                            <div class="progress-bar bg-${this.getStatusColor(job.status)}" 
                                 style="width: ${job.progress_percentage}%">
                                ${job.progress_percentage}%
                            </div>
                        </div>
                    </td>
                    <td>
                        <small>
                            Total: ${job.total_records.toLocaleString()}<br>
                            Success: <span class="text-success">${job.successful_records.toLocaleString()}</span><br>
                            Failed: <span class="text-danger">${job.failed_records.toLocaleString()}</span>
                        </small>
                    </td>
                    <td>
                        <span class="badge bg-${successRate > 90 ? 'success' : successRate > 70 ? 'warning' : 'danger'}">
                            ${successRate}%
                        </span>
                    </td>
                    <td>
                        <small>${job.started_at ? new Date(job.started_at).toLocaleString() : '-'}</small>
                    </td>
                    <td>${duration}</td>
                </tr>
            `;
        }).join('');
    }
    
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${this.escapeHtml(message)}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    escapeHtml(text) {
        if (typeof text !== 'string') return text;
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ProductImporter();
});