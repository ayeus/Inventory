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
        .then(data => {
            console.log("Data received:", data);
            const thead = document.querySelector('#inventory-table thead');
            const tbody = document.querySelector('#inventory-table tbody');
            if (!thead || !tbody) {
                console.log("Table head or body not found");
                return;
            }
            // Clear existing content
            thead.innerHTML = '';
            tbody.innerHTML = '';
            
            if (!Array.isArray(data) || data.length === 0) {
                console.log("No data to display for category:", category);
                thead.innerHTML = '<tr><th>No Data</th></tr>';
                tbody.innerHTML = '<tr><td>No items found for this category.</td></tr>';
                return;
            }
            
            // Generate table headers dynamically
            const headerRow = document.createElement('tr');
            const columns = Object.keys(data[0]);
            columns.forEach(column => {
                const th = document.createElement('th');
                th.textContent = column.replace('_', ' ').replace(/\b\w/g, char => char.toUpperCase());
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            
            // Generate table rows
            data.forEach(item => {
                const row = document.createElement('tr');
                columns.forEach(column => {
                    const td = document.createElement('td');
                    const value = item[column];
                    td.textContent = value !== null ? value : 'N/A';
                    row.appendChild(td);
                });
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading table:', error);
            const thead = document.querySelector('#inventory-table thead');
            const tbody = document.querySelector('#inventory-table tbody');
            if (thead && tbody) {
                thead.innerHTML = '<tr><th>Error</th></tr>';
                tbody.innerHTML = '<tr><td>Error loading data. Check the console for details.</td></tr>';
            }
        });
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
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            console.log("Form submission result:", result);
            document.getElementById('message').textContent = result.message;
            if (result.success) {
                const category = document.getElementById('category').value;
                loadTable(category);
                form.reset();
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            document.getElementById('message').textContent = 'Error submitting form';
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
        // Initial load is handled by server-side rendering
    } else {
        console.log("Category select not found");
    }

    if (document.getElementById('sales-form')) {
        handleFormSubmit('sales-form', '/sales_reform');
    }
    if (document.getElementById('restock-form')) {
        handleFormSubmit('restock-form', '/stock_counter');
    }
});