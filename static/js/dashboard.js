// Tab navigation
document.querySelectorAll('nav a').forEach(tab => {
    tab.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Deactivate all tabs
        document.querySelectorAll('nav a').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Activate clicked tab
        this.classList.add('active');
        document.getElementById(this.getAttribute('data-tab')).classList.add('active');
    });
});

// Dashboard charts
let statusChart, breedChart, ageChart;

function loadDashboardData() {
    fetch('/api/dashboard/pet-stats')
        .then(response => response.json())
        .then(data => {
            // Create charts
            createStatusChart(data.status_counts);
            createBreedChart(data.breed_counts);
            createAgeChart(data.age_distribution);
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
        });
}

function createStatusChart(data) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    if (statusChart) {
        statusChart.destroy();
    }
    
    statusChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(item => item.status),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: ['#4CAF50', '#FF9800']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function createBreedChart(data) {
    const ctx = document.getElementById('breedChart').getContext('2d');
    
    if (breedChart) {
        breedChart.destroy();
    }
    
    breedChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.breed),
            datasets: [{
                label: 'Pet Count by Breed',
                data: data.map(item => item.count),
                backgroundColor: '#2e5bff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function createAgeChart(data) {
    const ctx = document.getElementById('ageChart').getContext('2d');
    
    if (ageChart) {
        ageChart.destroy();
    }
    
    ageChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(item => item.age_group),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Pets table
function loadPets() {
    const statusFilter = document.getElementById('statusFilter').value;
    let url = '/pets';
    
    if (statusFilter !== 'all') {
        url += `?status=${statusFilter}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#petsTable tbody');
            tableBody.innerHTML = '';
            
            if (data.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="6" class="text-center">No pets found</td>';
                tableBody.appendChild(row);
                return;
            }
            
            data.forEach(pet => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${pet.pet_id}</td>
                    <td>${pet.name}</td>
                    <td>${pet.breed}</td>
                    <td>${pet.age}</td>
                    <td>${pet.status}</td>
                    <td>${pet.added_date}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading pets:', error);
        });
}

// Search functionality
document.getElementById('petSearch').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const rows = document.querySelectorAll('#petsTable tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
});

// Status filter
document.getElementById('statusFilter').addEventListener('change', loadPets);

// Refresh button
document.getElementById('refreshPets').addEventListener('click', loadPets);

// ETL functionality
const csvForm = document.getElementById('csvUploadForm');
const previewBtn = document.getElementById('previewBtn');
const uploadBtn = document.getElementById('uploadBtn');
const csvFileInput = document.getElementById('csvFile');
const loadingIndicator = document.getElementById('loadingIndicator');
const messageBox = document.getElementById('messageBox');
const previewCard = document.getElementById('previewCard');
const lastEtlRun = document.getElementById('lastEtlRun');

previewBtn.addEventListener('click', function() {
    if (!csvFileInput.files.length) {
        showMessage('Please select a CSV file first', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', csvFileInput.files[0]);
    
    loadingIndicator.classList.remove('hidden');
    messageBox.classList.add('hidden');
    
    fetch('/csv-preview', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loadingIndicator.classList.add('hidden');
        
        if (data.error) {
            showMessage(data.error, 'error');
            previewCard.classList.add('hidden');
            return;
        }
        
        // Create preview table
        const headerRow = document.createElement('tr');
        data.columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
        
        const previewHeader = document.querySelector('#previewTable thead');
        previewHeader.innerHTML = '';
        previewHeader.appendChild(headerRow);
        
        const previewBody = document.querySelector('#previewTable tbody');
        previewBody.innerHTML = '';
        
        data.data.forEach(row => {
            const tr = document.createElement('tr');
            data.columns.forEach(column => {
                const td = document.createElement('td');
                td.textContent = row[column] || '';
                tr.appendChild(td);
            });
            previewBody.appendChild(tr);
        });
        
        previewCard.classList.remove('hidden');
    })
    .catch(error => {
        loadingIndicator.classList.add('hidden');
        showMessage('Error previewing CSV: ' + error, 'error');
    });
});

csvForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (!csvFileInput.files.length) {
        showMessage('Please select a CSV file first', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', csvFileInput.files[0]);
    
    loadingIndicator.classList.remove('hidden');
    messageBox.classList.add('hidden');
    
    fetch('/upload-csv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loadingIndicator.classList.add('hidden');
        
        if (data.error) {
            showMessage(data.error, 'error');
        } else {
            showMessage(data.message, 'success');
            csvForm.reset();
            previewCard.classList.add('hidden');
            
            // Update last ETL run time
            const now = new Date();
            lastEtlRun.textContent = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
            
            // Reload pets data if on pets tab
            if (document.getElementById('pets').classList.contains('active')) {
                loadPets();
            }
            
            // Reload dashboard data if on dashboard tab
            if (document.getElementById('dashboard').classList.contains('active')) {
                loadDashboardData();
            }
        }
    })
    .catch(error => {
        loadingIndicator.classList.add('hidden');
        showMessage('Error uploading file: ' + error, 'error');
    });
});

function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = type;
    messageBox.classList.remove('hidden');
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadPets();
});