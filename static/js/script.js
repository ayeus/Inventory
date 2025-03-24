function loadTable(category) {
    console.log("loadTable called with category:", category);
    if (!category) {
        console.log("No category provided, aborting loadTable");
        return;
    }
    fetch(`/api/inventory/${category}`)
        .then(response => {
            console.log("Fetch response status:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(grid_data => {
            console.log("Data received:", grid_data);
            const tbody = document.querySelector('#inventory-table tbody');
            if (!tbody) {
                console.log("Table body not found");
                return;
            }
            // Clear existing content
            tbody.innerHTML = '';
            
            if (!grid_data || grid_data.length === 0) {
                console.log("No data to display for category:", category);
                tbody.innerHTML = '<tr><td>No data available for this category.</td></tr>';
                // Clear the form if no data
                updateStockForm([]);
                return;
            }
            
            // Generate table rows
            grid_data.forEach(row => {
                const tr = document.createElement('tr');
                row.forEach(cell => {
                    const td = document.createElement('td');
                    td.textContent = cell;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });

            // Update the stock form with the headers (first row of grid_data)
            updateStockForm(grid_data[0] || []);
        })
        .catch(error => {
            console.error('Error loading table:', error);
            const tbody = document.querySelector('#inventory-table tbody');
            if (tbody) {
                tbody.innerHTML = '<tr><td>Error loading data. Check the console for details.</td></tr>';
            }
            updateStockForm([]);
        });
}

function updateStockForm(headers) {
    console.log("Updating stock form with headers:", headers);
    const form = document.getElementById('stock-form');
    if (!form) {
        console.log("Stock form not found");
        return;
    }

    // Find the category input and the submit button
    const categoryInput = form.querySelector('input[name="category"]');
    const submitButton = form.querySelector('button[name="add_entry"]');
    const messageDiv = document.getElementById('message');

    // Clear existing form fields (except category and submit button)
    form.innerHTML = '';
    if (categoryInput) {
        form.appendChild(categoryInput);
    }

    // Add new input fields based on headers
    if (headers.length === 0) {
        const p = document.createElement('p');
        p.textContent = 'No columns available for this category.';
        form.appendChild(p);
    } else {
        const formContainer = document.createElement('div');
        formContainer.className = 'form-container';
        headers.forEach(header => {
            // Skip null/empty headers (should already be filtered by the server, but double-check)
            if (!header || header.trim() === '') {
                console.log("Skipping empty header:", header);
                return;
            }

            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';

            const label = document.createElement('label');
            const fieldName = header.replace(/[\s\.]/g, '_').toLowerCase();
            label.setAttribute('for', fieldName);
            label.textContent = header;
            formGroup.appendChild(label);

            const input = document.createElement('input');
            input.type = 'text';
            input.id = fieldName;
            input.name = fieldName;
            input.required = true;
            formGroup.appendChild(input);

            formContainer.appendChild(formGroup);
        });
        form.appendChild(formContainer);
    }

    // Re-append the submit button
    if (submitButton) {
        form.appendChild(submitButton);
    }

    // Re-append the message div
    if (messageDiv) {
        form.appendChild(messageDiv);
    }
}

function handleFormSubmit(formId, endpoint) {
    console.log("handleFormSubmit called for form:", formId);
    const form = document.getElementById(formId);
    if (!form) {
        console.log("Form not found:", formId);
        return;
    }
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        console.log("Submitting form data:", Object.fromEntries(formData));
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log("Response status:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            console.log("Form submission result:", result);
            document.getElementById('message').textContent = result.message;
            if (result.success) {
                form.reset();
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            document.getElementById('message').textContent = 'Error submitting form: ' + error.message;
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded, initializing script");
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        console.log("Category select found, value:", categorySelect.value);
        categorySelect.addEventListener('change', (e) => {
            console.log("Category changed to:", e.target.value);
            const form = categorySelect.closest('form');
            form.submit();
        });
        // Initial load of the table and form
        loadTable(categorySelect.value);
    } else {
        console.log("Category select not found");
    }

    if (document.getElementById('sales-form')) {
        handleFormSubmit('sales-form', '/sales_reform');
    }
    if (document.getElementById('stock-form')) {
        handleFormSubmit('stock-form', '/stock_counter');
    }
});