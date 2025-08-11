
        // Global variables
        let allEndpoints = [];
        let filteredEndpoints = [];
        let selectedEndpoint = null;

        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
            loadEndpoints();
            setupEventListeners();
        });

        // Load endpoints from the server
        function loadEndpoints() {
            fetch('/api/endpoints')
                .then(response => response.json())
                .then(data => {
                    allEndpoints = data.endpoints || [];
                    filteredEndpoints = [...allEndpoints];
                    updateTable();
                    updateStats();
                    populateAppFilter();
                })
                .catch(error => {
                    console.error('Error loading endpoints:', error);
                    document.getElementById('apiTableBody').innerHTML = 
                        '<tr><td colspan="4" class="no-results">Error loading endpoints</td></tr>';
                });
        }

        // Setup event listeners
        function setupEventListeners() {
            document.getElementById('appFilter').addEventListener('change', filterEndpoints);
            document.getElementById('methodFilter').addEventListener('change', filterEndpoints);
            document.getElementById('searchInput').addEventListener('input', filterEndpoints);
            document.getElementById('exportPostmanBtn').addEventListener('click', exportToPostman);
            
            // Add event delegation for copy buttons and row clicks
            document.addEventListener('click', function(e) {
                // Handle copy button clicks
                if (e.target.closest('.copy-btn')) {
                    e.stopPropagation(); // Prevent row click
                    const button = e.target.closest('.copy-btn');
                    const commandId = button.getAttribute('data-command');
                    const commandElement = document.getElementById(commandId);
                    if (commandElement) {
                        copyToClipboard(button, commandElement.textContent);
                    }
                    return;
                }
                
                // Handle close button clicks
                if (e.target.closest('.close-btn')) {
                    e.stopPropagation(); // Prevent row click
                    closeDetails();
                    return;
                }
                
                // Handle row clicks (only if not clicking on buttons)
                if (e.target.closest('tr') && !e.target.closest('button')) {
                    const row = e.target.closest('tr');
                    const rowIndex = Array.from(row.parentNode.children).indexOf(row);
                    if (rowIndex >= 0 && rowIndex < filteredEndpoints.length) {
                        const endpoint = filteredEndpoints[rowIndex];
                        toggleEndpointDetails(endpoint, row);
                    }
                }
            });
        }

        // Filter endpoints based on current filters
        function filterEndpoints() {
            const appFilter = document.getElementById('appFilter').value;
            const methodFilter = document.getElementById('methodFilter').value;
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();

            filteredEndpoints = allEndpoints.filter(endpoint => {
                // App filter
                if (appFilter && endpoint.app_name !== appFilter) {
                    return false;
                }

                // Method filter
                if (methodFilter) {
                    const methods = Array.isArray(endpoint.methods) ? endpoint.methods : [endpoint.methods];
                    if (!methods.some(method => method.toUpperCase() === methodFilter)) {
                        return false;
                    }
                }

                // Search filter
                if (searchTerm) {
                    const searchFields = [
                        endpoint.path || '',
                        endpoint.name || '',
                        endpoint.app_name || '',
                        (endpoint.methods || []).join(' ')
                    ];
                    if (!searchFields.some(field => field.toLowerCase().includes(searchTerm))) {
                        return false;
                    }
                }

                return true;
            });

            updateTable();
            updateStats();
        }

        // Update the API table
        function updateTable() {
            const tbody = document.getElementById('apiTableBody');
            tbody.innerHTML = '';

            if (filteredEndpoints.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="no-results">No endpoints found</td></tr>';
                return;
            }

            filteredEndpoints.forEach((endpoint, index) => {
                const row = document.createElement('tr');
                row.setAttribute('data-endpoint-index', index);
                
                const methods = Array.isArray(endpoint.methods) ? endpoint.methods : [endpoint.methods];
                const methodBadges = methods.map(method => 
                    `<span class="method-badge method-${method.toUpperCase()}">${method.toUpperCase()}</span>`
                ).join('');

                row.innerHTML = `
                    <td>
                        <div class="endpoint-path">${endpoint.full_url || endpoint.path}</div>
                    </td>
                    <td>
                        <div class="methods-container">${methodBadges}</div>
                    </td>
                    <td>${endpoint.name || '-'}</td>
                    <td>
                        <span class="app-name">${endpoint.app_name || '-'}</span>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        }

        // Update statistics
        function updateStats() {
            document.getElementById('totalApis').textContent = allEndpoints.length;
            document.getElementById('filteredApis').textContent = filteredEndpoints.length;
            
            const appFilter = document.getElementById('appFilter').value;
            document.getElementById('selectedApp').textContent = appFilter || 'All';
        }

        // Populate app filter dropdown
        function populateAppFilter() {
            const appFilter = document.getElementById('appFilter');
            const apps = [...new Set(allEndpoints.map(ep => ep.app_name).filter(Boolean))].sort();
            
            apps.forEach(app => {
                const option = document.createElement('option');
                option.value = app;
                option.textContent = app;
                appFilter.appendChild(option);
            });
        }

        // Toggle endpoint details (shutter/drawer)
        function toggleEndpointDetails(endpoint, row) {
            
            // Remove any existing details rows
            const existingDetails = document.querySelectorAll('.details-row');
            existingDetails.forEach(detail => detail.remove());
            
            // Remove selected class from all rows
            document.querySelectorAll('.api-table tr').forEach(tr => {
                tr.classList.remove('selected');
            });
            
            // If clicking the same row, just close it
            if (selectedEndpoint === endpoint) {
                selectedEndpoint = null;
                return;
            }
            
            selectedEndpoint = endpoint;
            row.classList.add('selected');
            
            // Create details row
            const detailsRow = document.createElement('tr');
            detailsRow.className = 'details-row';
            
            const methods = Array.isArray(endpoint.methods) ? endpoint.methods : [endpoint.methods];
            const fullUrl = endpoint.full_url || endpoint.path;
            
            // Generate parameter information
            let paramContent = '';
            if (endpoint.url_params && endpoint.url_params.length > 0) {
                paramContent = `
                    <div class="params-section">
                        <h3><i class="fas fa-link"></i> URL Parameters</h3>
                        <div class="params-container">
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Format</th>
                                        <th>Description</th>
                                        <th>Sample Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                `;
                
                endpoint.url_params.forEach(param => {
                    const paramName = typeof param === 'string' ? param : param.name;
                    const descriptiveName = typeof param === 'string' ? param : (param.descriptive_name || param.name);
                    const paramType = typeof param === 'string' ? 'string' : (param.type || 'string');
                    const paramFormat = typeof param === 'string' ? 'string' : (param.format || 'string');
                    const description = typeof param === 'string' ? `Parameter: ${param}` : (param.description || `Parameter: ${paramName}`);
                    const sampleValue = generateSampleValueForParam(param);
                    
                    paramContent += `
                        <tr>
                            <td><code>${paramName}</code></td>
                            <td><span class="param-type">${paramType}</span></td>
                            <td><span class="param-format">${paramFormat}</span></td>
                            <td>${description}</td>
                            <td><code class="sample-value">${sampleValue}</code></td>
                        </tr>
                    `;
                });
                
                paramContent += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }
            
            let curlContent = '';
            methods.forEach((method, index) => {
                const curlCommand = generateCurlCommand(fullUrl, method, endpoint);
                const commandId = `curl-${Date.now()}-${index}`;
                curlContent += `
                    <div class="curl-section">
                        <h3>${method.toUpperCase()} Request</h3>
                        <div class="curl-container">
                            <div class="curl-header">
                                <span class="curl-method">${method.toUpperCase()}</span>
                                <button class="copy-btn" data-command="${commandId}">
                                    <i class="fas fa-copy"></i> Copy
                                </button>
                            </div>
                            <div class="curl-code" id="${commandId}">${curlCommand}</div>
                        </div>
                    </div>
                `;
            });
            
            detailsRow.innerHTML = `
                <td colspan="4">
                    <div class="details-content">
                        <div class="details-header">
                            <div class="details-title">${endpoint.name || endpoint.path}</div>
                            <button class="close-btn" onclick="closeDetails()">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </div>
                        ${paramContent}
                        ${curlContent}
                    </div>
                </td>
            `;
            
            // Insert details row after the clicked row
            row.parentNode.insertBefore(detailsRow, row.nextSibling);
        }

        // Close details panel
        function closeDetails() {
            const existingDetails = document.querySelectorAll('.details-row');
            existingDetails.forEach(detail => detail.remove());
            document.querySelectorAll('.api-table tr').forEach(tr => {
                tr.classList.remove('selected');
            });
            selectedEndpoint = null;
        }

        // Generate cURL command
        function generateCurlCommand(url, method, endpoint) {
            // Clean and prepare the URL
            let cleanUrl = url;
            
            // Replace URL parameters with sample values
            if (endpoint.url_params && endpoint.url_params.length > 0) {
                endpoint.url_params.forEach(param => {
                    // Handle both old string format and new object format
                    const paramName = typeof param === 'string' ? param : param.name;
                    const sampleValue = generateSampleValueForParam(param);
                    cleanUrl = cleanUrl.replace(`{${paramName}}`, sampleValue);
                    cleanUrl = cleanUrl.replace(`<${paramName}>`, sampleValue);
                    cleanUrl = cleanUrl.replace(`(?P<${paramName}>[^)]*)`, sampleValue);
                });
            }
            
            // Handle query parameters for GET requests
            if (method.toUpperCase() === 'GET' && endpoint.url_params && endpoint.url_params.length > 0) {
                const queryParams = endpoint.url_params
                    .filter(param => {
                        const paramName = typeof param === 'string' ? param : param.name;
                        return !cleanUrl.includes(`{${paramName}}`) && !cleanUrl.includes(`<${paramName}}`);
                    })
                    .map(param => {
                        const paramName = typeof param === 'string' ? param : param.name;
                        return `${paramName}=${generateSampleValueForParam(param)}`;
                    })
                    .join('&');
                
                if (queryParams) {
                    cleanUrl += (cleanUrl.includes('?') ? '&' : '?') + queryParams;
                }
            }
            
            const baseCommand = `curl -X ${method.toUpperCase()} "${cleanUrl}"`;
            
            // Build headers
            const headers = [];
            headers.push('"Content-Type: application/json"');
            
            // Add authentication headers based on endpoint
            const endpointPath = endpoint.path || '';
            if (endpointPath.includes('auth') || endpointPath.includes('login') || endpointPath.includes('token')) {
                // For auth endpoints, use basic auth or no auth
                if (endpointPath.includes('login') || endpointPath.includes('register')) {
                    // No auth header for login/register
                } else {
                    headers.push('"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"');
                }
            } else {
                // For all other endpoints, use comprehensive auth
                headers.push('"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE3MzY5OTU4MDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"');
                headers.push('"X-API-Key: api_key_123456789abcdef"');
                headers.push('"X-Client-ID: client_987654321fedcba"');
                headers.push('"X-Request-ID: req_123456789abcdef"');
            }
            
            // Add method-specific headers
            if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
                headers.push('"Accept: application/json"');
                headers.push('"X-Content-Type: application/json"');
            }
            
            // Add common headers
            headers.push('"User-Agent: Django-API-Explorer/1.0"');
            headers.push('"Cache-Control: no-cache"');
            
            // Generate the cURL command
            let curlCommand = baseCommand;
            
            // Add headers
            headers.forEach(header => {
                curlCommand += ` \\\n  -H ${header}`;
            });
            
            // Add data for POST/PUT/PATCH requests
            if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
                const samplePayload = generateSamplePayload(endpoint);
                const escapedPayload = escapeJsonForShell(JSON.stringify(samplePayload, null, 2));
                curlCommand += ` \\\n  -d '${escapedPayload}'`;
            }
            
            return curlCommand;
        }

        // Generate sample value for URL parameter
        function generateSampleValueForParam(param) {
            // Handle both old string format and new object format
            let paramName, paramType, paramFormat;
            
            if (typeof param === 'string') {
                paramName = param;
                paramType = 'string';
                paramFormat = 'string';
            } else {
                paramName = param.name || param.descriptive_name || 'param';
                paramType = param.type || 'string';
                paramFormat = param.format || 'string';
            }
            
            const paramLower = paramName.toLowerCase();
            
            // Use parameter type and format if available (priority 1)
            if (paramType === 'integer') {
                if (paramLower.includes('page') || paramLower.includes('offset')) {
                    return '1';
                } else if (paramLower.includes('limit') || paramLower.includes('size') || paramLower.includes('count')) {
                    return '10';
                } else {
                    return '1';
                }
            }
            
            if (paramFormat === 'uuid') {
                return '123e4567-e89b-12d3-a456-426614174000';
            }
            
            if (paramFormat === 'email') {
                return 'user@example.com';
            }
            
            if (paramFormat === 'date') {
                return '2024-01-01';
            }
            
            if (paramFormat === 'date-time') {
                return '2024-01-01T00:00:00Z';
            }
            
            if (paramFormat === 'slug') {
                return 'sample-slug';
            }
            
            // Generate based on parameter name (priority 2)
            if (paramLower.includes('id') || paramLower.includes('pk')) {
                return Math.floor(Math.random() * 1000) + 1;
            } else if (paramLower.includes('uuid')) {
                return '550e8400-e29b-41d4-a716-446655440000';
            } else if (paramLower.includes('email')) {
                return 'user@example.com';
            } else if (paramLower.includes('name')) {
                return 'sample_name';
            } else if (paramLower.includes('slug')) {
                return 'sample-slug';
            } else if (paramLower.includes('date')) {
                return '2024-01-01';
            } else if (paramLower.includes('count') || paramLower.includes('limit')) {
                return Math.floor(Math.random() * 100) + 1;
            } else if (paramLower.includes('page')) {
                return Math.floor(Math.random() * 10) + 1;
            } else if (paramLower.includes('username')) {
                return 'sample_user';
            } else if (paramLower.includes('token')) {
                return 'your_token_here';
            } else if (paramLower.includes('format')) {
                return 'json';
            } else if (paramLower.includes('search') || paramLower.includes('query')) {
                return 'sample';
            } else if (paramLower.includes('start') || paramLower.includes('end')) {
                return '2024-01-01';
            }
            
            // Generate based on parameter type (priority 3)
            switch (paramType) {
                case 'integer':
                    return Math.floor(Math.random() * 1000) + 1;
                case 'string':
                    return `sample_${paramName}_${Math.floor(Math.random() * 100) + 1}`;
                case 'uuid':
                    return '550e8400-e29b-41d4-a716-446655440000';
                case 'email':
                    return 'user@example.com';
                case 'date':
                    return '2024-01-01';
                default:
                    return `sample_${paramName}`;
            }
        }
        
        // Escape JSON for shell compatibility
        function escapeJsonForShell(jsonString) {
            return jsonString
                .replace(/'/g, "'\"'\"'")  // Escape single quotes
                .replace(/\n/g, '\\n')     // Escape newlines
                .replace(/\r/g, '\\r')     // Escape carriage returns
                .replace(/\t/g, '\\t');    // Escape tabs
        }
        
        // Generate comprehensive sample payload with all possible fields
        function generateSamplePayload(endpoint) {
            const path = endpoint.path || '';
            const method = Array.isArray(endpoint.methods) ? endpoint.methods[0] : endpoint.methods;
            
            // Generate realistic sample data based on endpoint type
            const pathLower = path.toLowerCase();
            
            // User-related endpoints
            if (pathLower.includes('user') || pathLower.includes('profile') || pathLower.includes('account')) {
                if (method === 'POST') {
                    return {
                        username: `user_${Math.floor(Math.random() * 9000) + 1000}`,
                        email: 'user@example.com',
                        first_name: 'John',
                        last_name: 'Doe',
                        password: 'SecurePassword123!',
                        phone: '+1-555-123-4567',
                        date_of_birth: '1990-01-01',
                        is_active: true,
                        profile: {
                            bio: 'Software developer passionate about creating amazing applications.',
                            location: 'San Francisco, CA',
                            website: 'https://example.com',
                            social_links: {
                                twitter: '@johndoe',
                                linkedin: 'linkedin.com/in/johndoe',
                                github: 'github.com/johndoe'
                            }
                        }
                    };
                } else if (method === 'PUT' || method === 'PATCH') {
                    return {
                        first_name: 'John',
                        last_name: 'Doe',
                        email: 'user@example.com',
                        phone: '+1-555-123-4567',
                        profile: {
                            bio: 'Updated bio with new information.',
                            location: 'San Francisco, CA'
                        }
                    };
                }
            }
            
            // Product-related endpoints
            if (pathLower.includes('product') || pathLower.includes('item')) {
                if (method === 'POST') {
                    return {
                        name: `Product ${Math.floor(Math.random() * 900) + 100}`,
                        description: 'High-quality product designed for modern needs.',
                        price: (Math.random() * 1000 + 10).toFixed(2),
                        currency: 'USD',
                        category: 'Electronics',
                        brand: 'Tech Solutions',
                        sku: `SKU-${Math.floor(Math.random() * 90000) + 10000}`,
                        in_stock: true,
                        stock_quantity: Math.floor(Math.random() * 1000),
                        tags: ['featured', 'popular', 'trending'],
                        specifications: {
                            weight: '2.5 kg',
                            dimensions: '30x20x10 cm',
                            color: 'Black'
                        }
                    };
                } else if (method === 'PUT' || method === 'PATCH') {
                    return {
                        name: `Updated Product ${Math.floor(Math.random() * 900) + 100}`,
                        price: (Math.random() * 1000 + 10).toFixed(2),
                        description: 'Updated product description with new features.',
                        in_stock: true,
                        stock_quantity: Math.floor(Math.random() * 500) + 10
                    };
                }
            }
            
            // Order-related endpoints
            if (pathLower.includes('order') || pathLower.includes('purchase')) {
                if (method === 'POST') {
                    return {
                        customer_id: Math.floor(Math.random() * 9000) + 1000,
                        items: [
                            {
                                product_id: Math.floor(Math.random() * 100) + 1,
                                quantity: Math.floor(Math.random() * 5) + 1,
                                unit_price: (Math.random() * 200 + 10).toFixed(2)
                            }
                        ],
                        shipping_address: {
                            street: '123 Main Street',
                            city: 'New York',
                            state: 'NY',
                            zip_code: '10001',
                            country: 'United States'
                        },
                        payment_method: 'credit_card',
                        notes: 'Please deliver during business hours.'
                    };
                } else if (method === 'PUT' || method === 'PATCH') {
                    return {
                        status: 'processing',
                        tracking_number: `TRK${Math.floor(Math.random() * 900000000) + 100000000}`,
                        estimated_delivery: new Date(Date.now() + (7 + Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                    };
                }
            }
            
            // Article/blog endpoints
            if (pathLower.includes('article') || pathLower.includes('post') || pathLower.includes('blog')) {
                if (method === 'POST') {
                    return {
                        title: 'Amazing Article About Technology',
                        content: 'This is a comprehensive article about the latest developments in technology.',
                        excerpt: 'A brief summary of the article content.',
                        author_id: Math.floor(Math.random() * 100) + 1,
                        category: 'Technology',
                        tags: ['featured', 'trending', 'insights'],
                        status: 'published',
                        featured_image: 'https://example.com/images/article.jpg',
                        meta_description: 'SEO-friendly description for search engines.',
                        published_at: new Date().toISOString().split('T')[0]
                    };
                } else if (method === 'PUT' || method === 'PATCH') {
                    return {
                        title: 'Updated Article About Technology',
                        content: 'Updated content with new information and insights.',
                        status: 'published',
                        updated_at: new Date().toISOString()
                    };
                }
            }
            
            // Authentication endpoints
            if (pathLower.includes('auth') || pathLower.includes('login') || pathLower.includes('register')) {
                if (method === 'POST') {
                    if (pathLower.includes('login')) {
                        return {
                            username: 'johndoe',
                            password: 'SecurePassword123!',
                            remember_me: true
                        };
                    } else if (pathLower.includes('register')) {
                        return {
                            username: `user_${Math.floor(Math.random() * 9000) + 1000}`,
                            email: 'user@example.com',
                            password: 'SecurePassword123!',
                            password_confirm: 'SecurePassword123!',
                            first_name: 'John',
                            last_name: 'Doe'
                        };
                    } else if (pathLower.includes('password')) {
                        return {
                            email: 'user@example.com',
                            current_password: 'OldPassword123!',
                            new_password: 'NewSecurePassword456!',
                            new_password_confirm: 'NewSecurePassword456!'
                        };
                    }
                }
            }
            
            // File upload endpoints
            if (pathLower.includes('upload') || pathLower.includes('file')) {
                if (method === 'POST') {
                    return {
                        file: 'path/to/sample/file.pdf',
                        description: 'Sample file for testing purposes',
                        category: 'document',
                        tags: ['sample', 'test', 'upload'],
                        metadata: {
                            size: Math.floor(Math.random() * 10485760) + 1024, // 1KB to 10MB
                            format: 'pdf',
                            uploaded_by: Math.floor(Math.random() * 100) + 1
                        }
                    };
                }
            }
            
            // Campaign-related endpoints (keeping existing logic)
            if (path.includes('campaign')) {
                if (method === 'POST') {
                    return {
                        name: "Premium Gaming Campaign 2024",
                        description: "High-performance gaming campaign targeting competitive players",
                        status: "draft",
                        budget: 25000.00,
                        daily_budget: 1000.00,
                        start_date: "2024-01-01T00:00:00Z",
                        end_date: "2024-12-31T23:59:59Z",
                        target_audience: "competitive_gamers",
                        platform: "web",
                        ad_format: "banner",
                        targeting_criteria: {
                            age_range: "18-35",
                            locations: ["US", "CA", "UK", "DE"],
                            interests: ["gaming", "esports", "technology"],
                            device_types: ["desktop", "mobile"],
                            operating_systems: ["windows", "macos", "android", "ios"]
                        },
                        creative_assets: {
                            banner_url: "https://example.com/banner.jpg",
                            logo_url: "https://example.com/logo.png",
                            video_url: "https://example.com/video.mp4"
                        },
                        tracking_settings: {
                            conversion_tracking: true,
                            pixel_id: "123456789",
                            custom_parameters: {
                                utm_source: "gaming_campaign",
                                utm_medium: "banner",
                                utm_campaign: "premium_2024"
                            }
                        },
                        optimization_goals: ["clicks", "conversions", "reach"],
                        bid_strategy: "manual_cpc",
                        default_bid: 2.50,
                        is_active: true,
                        priority: "high",
                        tags: ["gaming", "premium", "competitive"],
                        notes: "Campaign for premium gaming audience",
                        created_by: "admin@example.com",
                        approved_by: "manager@example.com",
                        approval_status: "pending",
                        performance_metrics: {
                            impressions: 0,
                            clicks: 0,
                            conversions: 0,
                            spend: 0.00,
                            ctr: 0.00,
                            cpc: 0.00,
                            cpm: 0.00
                        }
                    };
                } else if (method === 'PUT' || method === 'PATCH') {
                    return {
                        name: "Updated Premium Gaming Campaign",
                        description: "Updated campaign description",
                        status: "active",
                        budget: 30000.00,
                        daily_budget: 1200.00,
                        end_date: "2024-12-31T23:59:59Z",
                        target_audience: "competitive_gamers",
                        bid_strategy: "auto_cpc",
                        default_bid: 3.00,
                        is_active: true,
                        priority: "high",
                        tags: ["gaming", "premium", "competitive", "updated"],
                        notes: "Campaign updated for better performance",
                        approval_status: "approved",
                        performance_metrics: {
                            impressions: 15000,
                            clicks: 750,
                            conversions: 25,
                            spend: 1875.00,
                            ctr: 5.00,
                            cpc: 2.50,
                            cpm: 125.00
                        }
                    };
                }
            } else if (path.includes('flight')) {
                if (method === 'POST') {
                    return {
                        name: "Q1 Gaming Flight",
                        campaign_id: 1,
                        campaign_name: "Premium Gaming Campaign 2024",
                        status: "scheduled",
                        start_date: "2024-01-01T00:00:00Z",
                        end_date: "2024-03-31T23:59:59Z",
                        budget: 7500.00,
                        daily_budget: 250.00,
                        targeting: {
                            age_range: "18-35",
                            locations: ["US", "CA"],
                            interests: ["gaming", "esports"],
                            device_types: ["desktop", "mobile"],
                            operating_systems: ["windows", "macos"],
                            languages: ["en", "es"],
                            time_zones: ["UTC-5", "UTC-8"],
                            custom_audiences: ["high_value_gamers", "esports_fans"],
                            lookalike_audiences: ["top_performers_1pct"],
                            excluded_audiences: ["existing_customers"]
                        },
                        ad_schedule: {
                            monday: { start: "09:00", end: "23:00" },
                            tuesday: { start: "09:00", end: "23:00" },
                            wednesday: { start: "09:00", end: "23:00" },
                            thursday: { start: "09:00", end: "23:00" },
                            friday: { start: "09:00", end: "23:00" },
                            saturday: { start: "10:00", end: "02:00" },
                            sunday: { start: "10:00", end: "02:00" }
                        },
                        creative_rotation: "optimize",
                        frequency_cap: {
                            impressions: 3,
                            period: "day"
                        },
                        bid_modifiers: {
                            mobile: 1.2,
                            desktop: 1.0,
                            weekend: 0.8,
                            evening: 1.1
                        },
                        is_active: true,
                        priority: "medium",
                        tags: ["q1", "gaming", "flight"],
                        notes: "Q1 flight for gaming campaign",
                        created_by: "campaign_manager@example.com",
                        performance_metrics: {
                            impressions: 0,
                            clicks: 0,
                            conversions: 0,
                            spend: 0.00,
                            ctr: 0.00,
                            cpc: 0.00,
                            cpm: 0.00,
                            reach: 0,
                            frequency: 0.00
                        }
                    };
                } else if (method === 'PUT' || method === 'PATCH') {
                    return {
                        name: "Updated Q1 Gaming Flight",
                        status: "active",
                        budget: 8000.00,
                        daily_budget: 300.00,
                        targeting: {
                            age_range: "18-35",
                            locations: ["US", "CA", "UK"],
                            interests: ["gaming", "esports", "technology"]
                        },
                        is_active: true,
                        performance_metrics: {
                            impressions: 5000,
                            clicks: 250,
                            conversions: 8,
                            spend: 625.00,
                            ctr: 5.00,
                            cpc: 2.50,
                            cpm: 125.00,
                            reach: 2000,
                            frequency: 2.5
                        }
                    };
                }
            } else if (path.includes('user') || path.includes('auth')) {
                if (path.includes('login')) {
                    return {
                        username: "testuser@example.com",
                        email: "testuser@example.com",
                        password: "SecurePassword123!",
                        remember_me: true,
                        two_factor_code: "123456",
                        device_id: "device_123456789",
                        ip_address: "192.168.1.100",
                        user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                    };
                } else if (path.includes('register')) {
                    return {
                        username: "newuser123",
                        email: "newuser@example.com",
                        password: "SecurePassword123!",
                        password_confirm: "SecurePassword123!",
                        first_name: "John",
                        last_name: "Doe",
                        phone_number: "+1-555-123-4567",
                        date_of_birth: "1990-01-15",
                        gender: "male",
                        country: "US",
                        state: "CA",
                        city: "San Francisco",
                        postal_code: "94105",
                        timezone: "America/Los_Angeles",
                        language: "en",
                        currency: "USD",
                        marketing_consent: true,
                        terms_accepted: true,
                        privacy_policy_accepted: true,
                        referral_code: "FRIEND123",
                        source: "organic",
                        utm_source: "google",
                        utm_medium: "cpc",
                        utm_campaign: "signup_campaign"
                    };
                } else if (method === 'POST') {
                    return {
                        username: "sample_user",
                        email: "user@example.com",
                        first_name: "John",
                        last_name: "Doe",
                        phone_number: "+1-555-123-4567",
                        date_of_birth: "1990-01-15",
                        gender: "male",
                        country: "US",
                        state: "CA",
                        city: "San Francisco",
                        postal_code: "94105",
                        address_line1: "123 Main Street",
                        address_line2: "Apt 4B",
                        timezone: "America/Los_Angeles",
                        language: "en",
                        currency: "USD",
                        is_active: true,
                        is_staff: false,
                        is_superuser: false,
                        email_verified: true,
                        phone_verified: true,
                        two_factor_enabled: false,
                        profile_picture: "https://example.com/avatar.jpg",
                        bio: "Passionate gamer and technology enthusiast",
                        website: "https://example.com",
                        social_links: {
                            twitter: "https://twitter.com/sample_user",
                            linkedin: "https://linkedin.com/in/sample_user",
                            github: "https://github.com/sample_user"
                        },
                        preferences: {
                            email_notifications: true,
                            sms_notifications: false,
                            push_notifications: true,
                            marketing_emails: true,
                            newsletter: true
                        },
                        tags: ["gamer", "tech_enthusiast", "early_adopter"]
                    };
                }
            } else if (path.includes('player') || path.includes('gamer')) {
                return {
                    username: "gamer123",
                    email: "gamer@example.com",
                    first_name: "Alex",
                    last_name: "Gamer",
                    phone_number: "+1-555-987-6543",
                    date_of_birth: "1995-06-20",
                    gender: "non_binary",
                    country: "US",
                    state: "NY",
                    city: "New York",
                    timezone: "America/New_York",
                    skill_level: "intermediate",
                    experience_years: 5,
                    preferred_games: ["FPS", "RPG", "MOBA", "Strategy"],
                    favorite_games: ["Counter-Strike", "League of Legends", "World of Warcraft"],
                    gaming_platforms: ["PC", "PlayStation", "Xbox", "Nintendo Switch"],
                    hardware_specs: {
                        cpu: "Intel i7-12700K",
                        gpu: "NVIDIA RTX 3080",
                        ram: "32GB DDR4",
                        storage: "1TB NVMe SSD",
                        monitor: "27\" 1440p 165Hz"
                    },
                    gaming_preferences: {
                        preferred_genres: ["FPS", "RPG", "Strategy"],
                        play_style: "competitive",
                        team_size: "5v5",
                        communication: "voice_chat",
                        time_commitment: "10-20_hours_week"
                    },
                    social_links: {
                        discord: "gamer123#1234",
                        steam: "steamcommunity.com/id/gamer123",
                        twitch: "twitch.tv/gamer123",
                        youtube: "youtube.com/@gamer123"
                    },
                    achievements: [
                        {
                            title: "First Victory",
                            description: "Won first competitive match",
                            date_earned: "2020-01-15",
                            game: "Counter-Strike"
                        }
                    ],
                    statistics: {
                        total_matches: 1500,
                        wins: 850,
                        losses: 650,
                        win_rate: 56.67,
                        average_score: 1250,
                        rank: "Gold",
                        level: 45
                    },
                    is_active: true,
                    last_login: "2024-01-15T10:30:00Z",
                    created_at: "2020-01-01T00:00:00Z",
                    updated_at: "2024-01-15T10:30:00Z"
                };
            } else if (path.includes('assessment') || path.includes('quiz')) {
                return {
                    title: "Advanced Gaming Skills Assessment",
                    description: "Comprehensive assessment to evaluate gaming skills and knowledge",
                    category: "gaming_skills",
                    difficulty: "intermediate",
                    time_limit: 30,
                    passing_score: 70,
                    max_attempts: 3,
                    is_active: true,
                    is_public: true,
                    tags: ["gaming", "skills", "assessment", "competitive"],
                    instructions: "Complete all questions within the time limit. Each question has only one correct answer.",
                    questions: [
                        {
                            id: 1,
                            question: "What is the primary objective in a Capture the Flag game mode?",
                            type: "multiple_choice",
                            options: [
                                "Eliminate all opponents",
                                "Capture the enemy flag and return it to your base",
                                "Control the most territory",
                                "Survive the longest"
                            ],
                            correct_answer: 1,
                            explanation: "Capture the Flag requires teams to steal the opponent's flag and bring it back to their own base.",
                            points: 10,
                            difficulty: "easy"
                        },
                        {
                            id: 2,
                            question: "Which of the following is NOT a common role in MOBA games?",
                            type: "multiple_choice",
                            options: [
                                "Carry",
                                "Support",
                                "Tank",
                                "Quarterback"
                            ],
                            correct_answer: 3,
                            explanation: "Quarterback is a football position, not a MOBA role.",
                            points: 10,
                            difficulty: "medium"
                        }
                    ],
                    prerequisites: ["basic_gaming_knowledge"],
                    target_audience: "intermediate_gamers",
                    estimated_completion_time: 30,
                    certificate_available: true,
                    certificate_name: "Gaming Skills Certificate",
                    created_by: "admin@example.com",
                    created_at: "2024-01-01T00:00:00Z",
                    updated_at: "2024-01-15T10:30:00Z",
                    version: "1.0",
                    metadata: {
                        total_questions: 2,
                        total_points: 20,
                        average_completion_time: 25,
                        pass_rate: 75.5
                    }
                };
            } else if (path.includes('booking') || path.includes('reservation')) {
                return {
                    service_id: 1,
                    service_name: "Premium Gaming Session",
                    user_id: 1,
                    user_name: "John Doe",
                    booking_date: "2024-01-15",
                    start_time: "14:00",
                    end_time: "16:00",
                    duration_hours: 2,
                    time_slot: "14:00-16:00",
                    location: "Virtual",
                    platform: "Discord",
                    session_type: "competitive_coaching",
                    coach_id: 5,
                    coach_name: "Pro Gamer Coach",
                    price: 100.00,
                    currency: "USD",
                    payment_status: "paid",
                    payment_method: "credit_card",
                    transaction_id: "txn_123456789",
                    status: "confirmed",
                    notes: "First session - focus on FPS fundamentals",
                    special_requirements: "Need voice chat setup",
                    equipment_needed: ["Gaming headset", "Microphone", "Stable internet"],
                    cancellation_policy: "24 hours notice required",
                    refund_policy: "Full refund if cancelled 24h in advance",
                    created_at: "2024-01-10T10:00:00Z",
                    updated_at: "2024-01-10T10:00:00Z",
                    reminder_sent: false,
                    feedback_submitted: false,
                    rating: null,
                    review: null
                };
            } else if (path.includes('invoice') || path.includes('billing')) {
                return {
                    invoice_number: "INV-2024-001",
                    customer_id: 1,
                    customer_name: "John Doe",
                    customer_email: "john.doe@example.com",
                    billing_address: {
                        street: "123 Main Street",
                        city: "San Francisco",
                        state: "CA",
                        postal_code: "94105",
                        country: "US"
                    },
                    items: [
                        {
                            description: "Premium Gaming Session",
                            quantity: 1,
                            unit_price: 100.00,
                            total_price: 100.00,
                            service_id: 1
                        },
                        {
                            description: "Gaming Assessment",
                            quantity: 1,
                            unit_price: 25.00,
                            total_price: 25.00,
                            service_id: 2
                        }
                    ],
                    subtotal: 125.00,
                    tax_rate: 0.085,
                    tax_amount: 10.63,
                    discount_amount: 0.00,
                    total_amount: 135.63,
                    currency: "USD",
                    payment_terms: "Net 30",
                    due_date: "2024-02-01",
                    issue_date: "2024-01-01",
                    status: "pending",
                    payment_status: "unpaid",
                    payment_method: null,
                    transaction_id: null,
                    notes: "Thank you for your business!",
                    terms_and_conditions: "Payment is due within 30 days of invoice date.",
                    created_at: "2024-01-01T00:00:00Z",
                    updated_at: "2024-01-01T00:00:00Z"
                };
            } else if (path.includes('token') || path.includes('auth')) {
                return {
                    access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                    refresh_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                    token_type: "Bearer",
                    expires_in: 3600,
                    expires_at: "2024-01-15T11:30:00Z",
                    scope: "read write",
                    user_id: 1,
                    username: "john.doe@example.com",
                    permissions: ["read", "write", "delete"],
                    device_info: {
                        device_id: "device_123456789",
                        device_type: "desktop",
                        browser: "Chrome",
                        os: "macOS",
                        ip_address: "192.168.1.100"
                    }
                };
            } else {
                // Generic comprehensive payload
                if (method === 'POST') {
                    return {
                        name: "Sample Item",
                        description: "A comprehensive sample item for testing purposes",
                        status: "active",
                        category: "sample",
                        priority: "medium",
                        tags: ["sample", "test", "dummy"],
                        metadata: {
                            created_by: "system",
                            version: "1.0",
                            environment: "development"
                        },
                        settings: {
                            is_public: true,
                            is_featured: false,
                            allow_comments: true,
                            moderation_required: false
                        },
                        timestamps: {
                            created_at: new Date().toISOString(),
                            updated_at: new Date().toISOString(),
                            published_at: null,
                            archived_at: null
                        },
                        relationships: {
                            parent_id: null,
                            children_ids: [],
                            related_ids: [1, 2, 3],
                            category_id: 1,
                            author_id: 1
                        },
                        custom_fields: {
                            field1: "value1",
                            field2: "value2",
                            field3: 123,
                            field4: true
                        }
                    };
                } else if (method === 'PUT' || method === 'PATCH') {
                    return {
                        name: "Updated Sample Item",
                        description: "Updated description for the sample item",
                        status: "updated",
                        priority: "high",
                        tags: ["sample", "test", "dummy", "updated"],
                        metadata: {
                            updated_by: "system",
                            version: "1.1",
                            change_reason: "Testing update functionality"
                        },
                        settings: {
                            is_featured: true,
                            moderation_required: true
                        },
                        timestamps: {
                            updated_at: new Date().toISOString()
                        }
                    };
                }
            }
            
            // Fallback comprehensive payload
            return {
                id: 1,
                name: "Comprehensive Sample Item",
                description: "This is a comprehensive sample item with all possible fields",
                status: "active",
                category: "sample",
                priority: "medium",
                tags: ["sample", "test", "comprehensive"],
                metadata: {
                    created_by: "system",
                    version: "1.0",
                    environment: "development",
                    last_modified: new Date().toISOString()
                },
                settings: {
                    is_public: true,
                    is_featured: false,
                    allow_comments: true,
                    moderation_required: false,
                    auto_approve: true
                },
                timestamps: {
                    created_at: "2024-01-01T00:00:00Z",
                    updated_at: new Date().toISOString(),
                    published_at: "2024-01-01T00:00:00Z",
                    archived_at: null
                },
                relationships: {
                    parent_id: null,
                    children_ids: [],
                    related_ids: [1, 2, 3],
                    category_id: 1,
                    author_id: 1,
                    owner_id: 1
                },
                custom_fields: {
                    field1: "value1",
                    field2: "value2",
                    field3: 123,
                    field4: true,
                    field5: ["item1", "item2", "item3"],
                    field6: {
                        nested_key: "nested_value",
                        nested_number: 456
                    }
                }
            };
        }

        // Copy to clipboard
        function copyToClipboard(button, text) {
            // Clean the text (remove extra backslashes and format properly)
            const cleanText = text.replace(/\\\s*\n\s*/g, ' \\\n  ');
            
            // Show immediate feedback
            showCopyAttempt(button);
            
            // Try modern clipboard API first
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(cleanText).then(() => {
                    showCopySuccess(button);
                }).catch(err => {
                    console.error('Clipboard API failed:', err);
                    fallbackCopy(button, cleanText);
                });
            } else {
                // Use fallback for non-secure contexts or older browsers
                fallbackCopy(button, cleanText);
            }
        }
        
        // Fallback copy method
        function fallbackCopy(button, text) {
            try {
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                const successful = document.execCommand('copy');
                document.body.removeChild(textArea);
                
                if (successful) {
                    showCopySuccess(button);
                } else {
                    showCopyError(button);
                }
            } catch (err) {
                console.error('Fallback copy failed:', err);
                showCopyError(button);
            }
        }
        
        // Show copy attempt (immediate feedback)
        function showCopyAttempt(button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Copying...';
            button.style.backgroundColor = '#ffc107';
            button.style.color = '#000';
            
            // Store original text for later restoration
            button._originalText = originalText;
        }
        
        // Show copy success
        function showCopySuccess(button) {
            button.innerHTML = '<i class="fas fa-check"></i> Copied!';
            button.classList.add('copied');
            button.style.backgroundColor = '#28a745';
            button.style.color = '#fff';
            
            setTimeout(() => {
                button.innerHTML = button._originalText || '<i class="fas fa-copy"></i> Copy';
                button.classList.remove('copied');
                button.style.backgroundColor = '';
                button.style.color = '';
                delete button._originalText;
            }, 2000);
        }
        
        // Show copy error
        function showCopyError(button) {
            button.innerHTML = '<i class="fas fa-times"></i> Failed';
            button.classList.add('copy-error');
            button.style.backgroundColor = '#dc3545';
            button.style.color = '#fff';
            
            setTimeout(() => {
                button.innerHTML = button._originalText || '<i class="fas fa-copy"></i> Copy';
                button.classList.remove('copy-error');
                button.style.backgroundColor = '';
                button.style.color = '';
                delete button._originalText;
            }, 2000);
        }

        // Export filtered endpoints to Postman collection
        function exportToPostman() {
            if (filteredEndpoints.length === 0) {
                alert('No endpoints to export. Please adjust your filters.');
                return;
            }

            const collection = generatePostmanCollection(filteredEndpoints);
            downloadPostmanCollection(collection);
        }

        // Generate Postman collection JSON
        function generatePostmanCollection(endpoints) {
            const baseUrl = getBaseUrl();
            const appFilter = document.getElementById('appFilter').value;
            const methodFilter = document.getElementById('methodFilter').value;
            const searchTerm = document.getElementById('searchInput').value;

            // Generate collection name based on filters
            let collectionName = 'Django API Collection';
            if (appFilter) {
                collectionName += ` - ${appFilter}`;
            }
            if (methodFilter) {
                collectionName += ` - ${methodFilter}`;
            }
            if (searchTerm) {
                collectionName += ` - "${searchTerm}"`;
            }

            const collection = {
                info: {
                    name: collectionName,
                    description: `Auto-generated Postman collection for Django APIs${appFilter ? ` (${appFilter} app)` : ''}`,
                    schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
                },
                variable: [
                    {
                        key: 'base_url',
                        value: baseUrl,
                        type: 'string'
                    },
                    {
                        key: 'auth_token',
                        value: 'your_auth_token_here',
                        type: 'string'
                    },
                    {
                        key: 'api_key',
                        value: 'your_api_key_here',
                        type: 'string'
                    }
                ],
                item: []
            };

            // Group endpoints by app for better organization
            const groupedEndpoints = groupEndpointsByApp(endpoints);

            Object.keys(groupedEndpoints).forEach(appName => {
                const appEndpoints = groupedEndpoints[appName];
                const appFolder = {
                    name: appName,
                    item: []
                };

                appEndpoints.forEach(endpoint => {
                    const methods = Array.isArray(endpoint.methods) ? endpoint.methods : [endpoint.methods];
                    
                    methods.forEach(method => {
                        const request = createPostmanRequest(endpoint, method, baseUrl);
                        appFolder.item.push(request);
                    });
                });

                collection.item.push(appFolder);
            });

            return collection;
        }

        // Group endpoints by app
        function groupEndpointsByApp(endpoints) {
            const grouped = {};
            
            endpoints.forEach(endpoint => {
                const appName = endpoint.app_name || 'Unknown App';
                if (!grouped[appName]) {
                    grouped[appName] = [];
                }
                grouped[appName].push(endpoint);
            });

            return grouped;
        }

        // Create a Postman request object
        function createPostmanRequest(endpoint, method, baseUrl) {
            const methodUpper = method.toUpperCase();
            const endpointPath = endpoint.path || '';
            const fullUrl = endpoint.full_url || endpoint.path;
            
            // Generate request name
            const requestName = `${methodUpper} ${endpoint.name || endpointPath}`;
            
            // Process URL with parameters
            let processedUrl = fullUrl;
            const urlParams = [];
            
            if (endpoint.url_params && endpoint.url_params.length > 0) {
                endpoint.url_params.forEach(param => {
                    const paramName = typeof param === 'string' ? param : param.name;
                    const sampleValue = generateSampleValueForParam(param);
                    
                    // Replace URL parameters
                    processedUrl = processedUrl.replace(`{${paramName}}`, `{{${paramName}}}`);
                    processedUrl = processedUrl.replace(`<${paramName}>`, `{{${paramName}}}`);
                    processedUrl = processedUrl.replace(`(?P<${paramName}>[^)]*)`, `{{${paramName}}}`);
                    
                    // Add as URL variable
                    urlParams.push({
                        key: paramName,
                        value: sampleValue,
                        description: typeof param === 'string' ? `Parameter: ${param}` : (param.description || `Parameter: ${paramName}`)
                    });
                });
            }

            // Build the request object
            const request = {
                name: requestName,
                request: {
                    method: methodUpper,
                    header: generatePostmanHeaders(endpoint, methodUpper),
                    url: {
                        raw: `{{base_url}}${processedUrl}`,
                        host: ['{{base_url}}'],
                        path: processedUrl.split('/').filter(segment => segment.length > 0)
                    },
                    description: endpoint.description || `API endpoint: ${endpointPath}`
                }
            };

            // Add URL variables if any
            if (urlParams.length > 0) {
                request.request.url.variable = urlParams;
            }

            // Add body for POST/PUT/PATCH requests
            if (['POST', 'PUT', 'PATCH'].includes(methodUpper)) {
                const samplePayload = generateSamplePayload(endpoint);
                request.request.body = {
                    mode: 'raw',
                    raw: JSON.stringify(samplePayload, null, 2),
                    options: {
                        raw: {
                            language: 'json'
                        }
                    }
                };
            }

            return request;
        }

        // Generate Postman headers
        function generatePostmanHeaders(endpoint, method) {
            const headers = [
                {
                    key: 'Content-Type',
                    value: 'application/json'
                },
                {
                    key: 'Accept',
                    value: 'application/json'
                }
            ];

            // Add authentication headers
            const endpointPath = endpoint.path || '';
            if (!endpointPath.includes('auth') && !endpointPath.includes('login') && !endpointPath.includes('register')) {
                headers.push({
                    key: 'Authorization',
                    value: 'Bearer {{auth_token}}'
                });
                headers.push({
                    key: 'X-API-Key',
                    value: '{{api_key}}'
                });
            }

            // Add method-specific headers
            if (['POST', 'PUT', 'PATCH'].includes(method)) {
                headers.push({
                    key: 'X-Content-Type',
                    value: 'application/json'
                });
            }

            // Add common headers
            headers.push({
                key: 'User-Agent',
                value: 'Django-API-Explorer/1.0'
            });
            headers.push({
                key: 'Cache-Control',
                value: 'no-cache'
            });

            return headers;
        }

        // Get base URL for the collection
        function getBaseUrl() {
            // Try to extract base URL from the first endpoint
            if (filteredEndpoints.length > 0) {
                const firstEndpoint = filteredEndpoints[0];
                if (firstEndpoint.full_url) {
                    const url = new URL(firstEndpoint.full_url);
                    return `${url.protocol}//${url.host}`;
                }
            }
            
            // Fallback to default
            return 'http://127.0.0.1:8000';
        }

        // Download Postman collection file
        function downloadPostmanCollection(collection) {
            const collectionJson = JSON.stringify(collection, null, 2);
            const blob = new Blob([collectionJson], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `${collection.info.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            // Show success message
            showExportSuccess();
        }

        // Show export success message
        function showExportSuccess() {
            const button = document.getElementById('exportPostmanBtn');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i> Exported!';
            button.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.background = 'linear-gradient(135deg, #ff6b35, #f7931e)';
            }, 2000);
        }
