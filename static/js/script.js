function loadTable(category) {
    console.log("loadTable called with category:", category);
    if (!category) {
        console.log("No category provided, aborting loadTable");
        return;
    }
    fetch(`/api/inventory/${category}`)
        .then(response => {
            console.log("Fetch response status for loadTable:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(grid_data => {
            console.log("Data received for table:", grid_data);
            const tbody = document.querySelector('#inventory-table tbody');
            if (!tbody) {
                console.log("Table body not found");
                return;
            }
            tbody.innerHTML = '';
            
            if (!grid_data || grid_data.length === 0) {
                console.log("No data to display for category:", category);
                tbody.innerHTML = '<tr><td>No data available for this category.</td></tr>';
                updateStockForm([]);
                return;
            }
            
            grid_data.forEach((row, rowIndex) => {
                const tr = document.createElement('tr');
                tr.className = 'editable';
                tr.dataset.rowIndex = rowIndex;
                row.forEach(cell => {
                    const td = document.createElement('td');
                    td.textContent = cell;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });

            updateStockForm(grid_data[0] || []);

            // Add click event listeners to editable rows
            document.querySelectorAll('.editable').forEach(row => {
                row.addEventListener('click', () => {
                    const rowIndex = row.dataset.rowIndex;
                    const cells = row.querySelectorAll('td');
                    const headers = grid_data[0];
                    const form = document.getElementById('stock-form');
                    form.querySelector('input[name="action"]').value = 'edit_entry';
                    form.querySelector('input[name="row_index"]').value = rowIndex;
                    headers.forEach((header, colIndex) => {
                        const fieldName = header.replace(/[\s\.]/g, '_').toLowerCase();
                        const input = form.querySelector(`input[name="${fieldName}"]`);
                        if (input) {
                            input.value = cells[colIndex].textContent;
                        }
                    });
                    document.getElementById('message').textContent = 'Editing row ' + rowIndex + '. Update the form and click "Add Entry" to save changes.';
                    document.getElementById('message').className = '';
                });
            });
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

    const categoryInput = form.querySelector('input[name="category"]');
    const actionInput = form.querySelector('input[name="action"]') || document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = 'add_entry';

    const rowIndexInput = form.querySelector('input[name="row_index"]') || document.createElement('input');
    rowIndexInput.type = 'hidden';
    rowIndexInput.name = 'row_index';
    rowIndexInput.value = '';

    form.innerHTML = '';
    if (categoryInput) {
        form.appendChild(categoryInput);
    }
    form.appendChild(actionInput);
    form.appendChild(rowIndexInput);

    if (headers.length === 0) {
        console.log("No headers provided for form");
        const p = document.createElement('p');
        p.textContent = 'No columns available for this category.';
        form.appendChild(p);
    } else {
        const formContainer = document.createElement('div');
        formContainer.className = 'form-container';
        headers.forEach(header => {
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

    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.textContent = 'Add Entry';
    form.appendChild(submitButton);

    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        form.appendChild(messageDiv);
    }
}

function handleFormSubmit(formId, endpoint) {
    console.log("handleFormSubmit called for form:", formId, "with endpoint:", endpoint);
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
            console.log("Fetch response status for form submission:", response.status);
            console.log("Response headers:", response.headers);
            if (!response.ok) {
                return response.text().then(text => {
                    console.error("Non-OK response received:", text);
                    throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
                });
            }
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                return response.text().then(text => {
                    console.error("Non-JSON response received:", text);
                    throw new Error('Expected JSON response, but received: ' + text);
                });
            }
            return response.json();
        })
        .then(result => {
            console.log("Form submission result:", result);
            const messageDiv = document.getElementById('message');
            if (!messageDiv) {
                console.log("Message div not found");
                return;
            }
            messageDiv.textContent = result.message;
            if (result.success) {
                messageDiv.className = 'success-message';
                form.reset();
                form.querySelector('input[name="action"]').value = 'add_entry';
                form.querySelector('input[name="row_index"]').value = '';
                const category = form.querySelector('input[name="category"]').value;
                console.log("Reloading table for category:", category);
                loadTable(category);
            } else {
                messageDiv.className = 'error-message';
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            const messageDiv = document.getElementById('message');
            if (messageDiv) {
                messageDiv.textContent = 'Failed to add/update item: ' + error.message;
                messageDiv.className = 'error-message';
            }
        });
    });
}

function handleDeleteCategory() {
    const form = document.getElementById('stock-form');
    if (!form) {
        console.log("Stock form not found for delete action");
        return;
    }
    const category = form.querySelector('input[name="category"]').value;
    if (!confirm(`Are you sure you want to delete all items in category "${category}"?`)) {
        return;
    }

    const formData = new FormData();
    formData.append('category', category);
    formData.append('action', 'delete_category');

    fetch('/stock_counter', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
            });
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return response.text().then(text => {
                throw new Error('Expected JSON response, but received: ' + text);
            });
        }
        return response.json();
    })
    .then(result => {
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = result.message;
        if (result.success) {
            messageDiv.className = 'success-message';
            // Reload the page to reflect the deleted category
            window.location.reload();
        } else {
            messageDiv.className = 'error-message';
        }
    })
    .catch(error => {
        console.error('Error deleting category:', error);
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = 'Failed to delete category: ' + error.message;
        messageDiv.className = 'error-message';
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
        loadTable(categorySelect.value);
    } else {
        console.log("Category select not found");
    }

    const stockForm = document.getElementById('stock-form');
    if (stockForm) {
        const endpoint = stockForm.getAttribute('data-endpoint') || '/stock_counter';
        handleFormSubmit('stock-form', endpoint);
    } else {
        console.log("Stock form not found on page load");
    }

    const deleteButton = document.getElementById('delete-category');
    if (deleteButton) {
        deleteButton.addEventListener('click', handleDeleteCategory);
    }

    if (document.getElementById('sales-form')) {
        handleFormSubmit('sales-form', '/sales_reform');
    }
});