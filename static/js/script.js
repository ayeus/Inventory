function loadTable(table) {
    console.log("loadTable called with table:", table);
    if (!table) {
        console.log("No table provided, aborting loadTable");
        return;
    }
    fetch(`/api/inventory/${table}`)
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
                console.log("No data to display for table:", table);
                tbody.innerHTML = '<tr><td>No data available for this table.</td></tr>';
                updateStockForm([]);
                return;
            }
            
            grid_data.forEach((row, rowIndex) => {
                const tr = document.createElement('tr');
                if (rowIndex > 0) {
                    tr.className = 'editable';
                    tr.dataset.rowId = row[0];  // Store the 'id' for editing/deleting
                }
                row.forEach((cell, cellIndex) => {
                    const td = document.createElement('td');
                    td.textContent = cell;
                    if (cellIndex === 1 && rowIndex > 0) {  // Place Delete button in the second column
                        const deleteButton = document.createElement('button');
                        deleteButton.className = 'delete-row-button';
                        deleteButton.textContent = 'Delete';
                        deleteButton.onclick = () => deleteRow(table, row[0]);
                        td.appendChild(deleteButton);
                    }
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });

            updateStockForm(grid_data[0] || []);

            // Add click event listeners to editable rows
            document.querySelectorAll('.editable').forEach(row => {
                row.addEventListener('click', (e) => {
                    if (e.target.className.includes('delete-row-button')) return;  // Ignore clicks on delete button
                    const rowId = row.dataset.rowId;
                    const cells = row.querySelectorAll('td');
                    const headers = grid_data[0];
                    const form = document.getElementById('stock-form');
                    form.querySelector('input[name="action"]').value = 'edit_entry';
                    form.querySelector('input[name="row_id"]').value = rowId;
                    headers.forEach((header, colIndex) => {
                        if (header === 'id') return;  // Skip 'id' column
                        const fieldName = header.replace(/[\s\.]/g, '_').toLowerCase();
                        const input = form.querySelector(`input[name="${fieldName}"]`);
                        if (input) {
                            input.value = cells[colIndex].textContent;
                        }
                    });
                    document.getElementById('message').textContent = 'Editing row with ID ' + rowId + '. Update the form and click "Add Entry" to save changes.';
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

    const tableInput = form.querySelector('input[name="table"]');
    const actionInput = form.querySelector('input[name="action"]') || document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = 'add_entry';

    const rowIdInput = form.querySelector('input[name="row_id"]') || document.createElement('input');
    rowIdInput.type = 'hidden';
    rowIdInput.name = 'row_id';
    rowIdInput.value = '';

    form.innerHTML = '';
    if (tableInput) {
        form.appendChild(tableInput);
    }
    form.appendChild(actionInput);
    form.appendChild(rowIdInput);

    if (headers.length === 0) {
        console.log("No headers provided for form");
        const p = document.createElement('p');
        p.textContent = 'No columns available for this table.';
        form.appendChild(p);
    } else {
        const formContainer = document.createElement('div');
        formContainer.className = 'form-container';
        headers.forEach(header => {
            if (header === 'id' || !header || header.trim() === '') {
                console.log("Skipping header:", header);
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
                form.querySelector('input[name="row_id"]').value = '';
                const table = form.querySelector('input[name="table"]').value;
                console.log("Reloading table for table:", table);
                loadTable(table);
            } else {
                messageDiv.className = 'error-message';
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            const messageDiv = document.getElementById('message');
            if (messageDiv) {
                messageDiv.textContent = 'Failed to process request: ' + error.message;
                messageDiv.className = 'error-message';
            }
        });
    });
}

function deleteRow(table, rowId) {
    if (!confirm(`Are you sure you want to delete the entry with ID ${rowId}?`)) {
        return;
    }

    const formData = new FormData();
    formData.append('table', table);
    formData.append('action', 'delete_entry');
    formData.append('row_id', rowId);

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
            loadTable(table);
        } else {
            messageDiv.className = 'error-message';
        }
    })
    .catch(error => {
        console.error('Error deleting row:', error);
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = 'Failed to delete row: ' + error.message;
        messageDiv.className = 'error-message';
    });
}

function handleDeleteAll() {
    const form = document.getElementById('stock-form');
    if (!form) {
        console.log("Stock form not found for delete action");
        return;
    }
    const table = form.querySelector('input[name="table"]').value;
    if (!table) {
        console.log("No table selected for delete all action");
        return;
    }
    if (!confirm(`Are you sure you want to delete all entries in table "${table}"?`)) {
        return;
    }

    const formData = new FormData();
    formData.append('table', table);
    formData.append('action', 'delete_all');

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
            loadTable(table);
        } else {
            messageDiv.className = 'error-message';
        }
    })
    .catch(error => {
        console.error('Error deleting all entries:', error);
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = 'Failed to delete all entries: ' + error.message;
        messageDiv.className = 'error-message';
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded, initializing script");
    const tableSelect = document.getElementById('table');
    if (tableSelect) {
        console.log("Table select found, value:", tableSelect.value);
        tableSelect.addEventListener('change', (e) => {
            e.preventDefault();  // Prevent default form submission
            const selectedTable = e.target.value;
            console.log("Table changed to:", selectedTable);
            
            // Update the hidden table input in the stock form
            const stockForm = document.getElementById('stock-form');
            if (stockForm) {
                const tableInput = stockForm.querySelector('input[name="table"]');
                if (tableInput) {
                    tableInput.value = selectedTable;
                }
            } else {
                console.log("Stock form not found");
            }
            
            // Load the table data dynamically
            loadTable(selectedTable);
        });
        if (tableSelect.value) {
            loadTable(tableSelect.value);
        } else {
            console.log("No table selected, skipping loadTable");
        }
    } else {
        console.log("Table select not found");
    }

    const stockForm = document.getElementById('stock-form');
    if (stockForm) {
        const endpoint = stockForm.getAttribute('data-endpoint') || '/stock_counter';
        handleFormSubmit('stock-form', endpoint);
    } else {
        console.log("Stock form not found on page load");
    }

    const deleteAllButton = document.getElementById('delete-all');
    if (deleteAllButton) {
        deleteAllButton.addEventListener('click', handleDeleteAll);
    } else {
        console.log("Delete all button not found");
    }

    if (document.getElementById('sales-form')) {
        handleFormSubmit('sales-form', '/sales_reform');
    }
});