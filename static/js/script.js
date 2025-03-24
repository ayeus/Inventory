function loadTable(category) {
    if (!category) return;
    fetch(`/api/inventory/${category}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#inventory-table tbody');
            if (!tbody) return;
            tbody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                const name = item['Item_description'] || item['Name of Items'] || item['Equipment’s'] || 'N/A';
                const stock = item['stock'] || item['QUANTITY (IN 2023-2024)'] || 0;
                row.innerHTML = `
                    <td>${item['S.No.'] || 'N/A'}</td>
                    <td>${name}</td>
                    <td>${stock}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading table:', error);
        });
}

function handleFormSubmit(formId, endpoint) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(result => {
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
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            const form = categorySelect.closest('form');
            form.submit();
        });
        loadTable(categorySelect.value);
    }

    if (document.getElementById('sales-form')) {
        handleFormSubmit('sales-form', '/sales_reform');
    }
    if (document.getElementById('restock-form')) {
        handleFormSubmit('restock-form', '/stock_counter');
    }
});