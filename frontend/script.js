console.log('Script started, attempting to fetch data...');

// Format date for better readability
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Group appliances for better display
function formatAppliances(applianceString) {
    if (!applianceString) return [];
    return applianceString.split(', ').map(app => app.trim());
}

fetch('/api/consumption')
    .then(res => {
        console.log('Response received:', res.status);
        if (!res.ok) {
            throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        console.log('Data received:', data.length, 'records');
        const div = document.getElementById('consumption-data');
        div.innerHTML = ''; // Clear loading message
        
        if (data.length === 0) {
            div.innerHTML = '<div class="error">No data available</div>';
            return;
        }
        
        // Sort data by timestamp (newest first)
        data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        // Create data items
        data.forEach(item => {
            const dataItem = document.createElement('div');
            dataItem.className = 'data-item';
            
            // Format timestamp
            const timestamp = document.createElement('div');
            timestamp.className = 'timestamp';
            timestamp.textContent = formatDate(item.timestamp);
            dataItem.appendChild(timestamp);
            
            // Format appliances
            const appliances = formatAppliances(item.appliance);
            if (appliances.length > 0) {
                const applianceContainer = document.createElement('div');
                applianceContainer.className = 'appliance-container';
                
                appliances.forEach(app => {
                    const applianceTag = document.createElement('span');
                    applianceTag.className = 'appliance';
                    applianceTag.textContent = app;
                    applianceContainer.appendChild(applianceTag);
                });
                
                dataItem.appendChild(applianceContainer);
            }
            
            // Format consumption
            const consumption = document.createElement('div');
            consumption.className = 'consumption';
            consumption.textContent = `Consumption: ${item.consumption.toFixed(2)} kWh`;
            dataItem.appendChild(consumption);
            
            div.appendChild(dataItem);
        });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        const div = document.getElementById('consumption-data');
        div.innerHTML = `<div class="error">Error loading data: ${error.message}. Please make sure the backend server is running.</div>`;
    });

function initializeDashboard() {
    // ... existing initialization code ...
}
