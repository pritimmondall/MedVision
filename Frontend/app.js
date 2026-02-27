const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const reportContent = document.getElementById('reportContent');

// Show file name when selected
fileInput.addEventListener('change', () => {
    const name = fileInput.files[0]?.name;
    document.getElementById('fileName').textContent = name ? `Selected: ${name}` : '';
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!fileInput.files[0]) return alert("Please select a file!");

    // 1. Prepare UI
    form.classList.add('hidden');
    loading.classList.remove('hidden');
    results.classList.add('hidden');

    // 2. Prepare Data
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('priority', document.getElementById('priority').value);

    try {
        // 3. Send to Backend
        // NOTE: The request will 'hang' here if the backend is waiting for 
        // your terminal input (Map Feature 'y/n'). Look at VS Code!
        const response = await fetch('http://127.0.0.1:8000/process-prescription', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // 4. Render Results
        displayResults(data);

    } catch (error) {
        alert("Error connecting to Agent: " + error.message);
        form.classList.remove('hidden'); // Show form again
    } finally {
        loading.classList.add('hidden');
    }
});

function displayResults(data) {
    results.classList.remove('hidden');
    
    // A. Render Calendar Logic
    const calCard = document.getElementById('calendarCard');
    if (data.calendar && data.calendar.status === 'success') {
        calCard.classList.remove('hidden');
        document.getElementById('calendarLink').href = data.calendar.link;
    } else {
        calCard.classList.add('hidden');
    }

    // B. Render Agent Report (Medicines, Tests, Next Visit)
    reportContent.innerHTML = '';
    
    // Show prescription data (medicines, tests, next_visit)
    const prescriptionData = data.data;
    if (prescriptionData) {
        // Medicines section
        if (prescriptionData.medicines && prescriptionData.medicines.length > 0) {
            const medHeader = document.createElement('h4');
            medHeader.textContent = '💊 Medicines';
            medHeader.style.marginBottom = '10px';
            reportContent.appendChild(medHeader);
            
            prescriptionData.medicines.forEach(med => {
                const div = document.createElement('div');
                div.className = 'order-item';
                div.innerHTML = `
                    <strong>${med.name}</strong><br>
                    <small style="color: #6b7280">${med.dosage}</small>
                `;
                reportContent.appendChild(div);
            });
        }
        
        // Tests section
        if (prescriptionData.tests && prescriptionData.tests.length > 0) {
            const testHeader = document.createElement('h4');
            testHeader.textContent = '🧪 Tests';
            testHeader.style.margin = '15px 0 10px';
            reportContent.appendChild(testHeader);
            
            prescriptionData.tests.forEach(test => {
                const div = document.createElement('div');
                div.className = 'order-item';
                div.innerHTML = `<span>${test}</span>`;
                reportContent.appendChild(div);
            });
        }
        
        // Next visit
        if (prescriptionData.next_visit) {
            const visitDiv = document.createElement('div');
            visitDiv.style.marginTop = '15px';
            visitDiv.innerHTML = `<strong>📅 Next Visit:</strong> ${prescriptionData.next_visit}`;
            reportContent.appendChild(visitDiv);
        }
    }
    
    // Show purchase report if available
    if (data.report && data.report.length > 0) {
        const purchaseHeader = document.createElement('h4');
        purchaseHeader.textContent = '🛒 Purchase Report';
        purchaseHeader.style.margin = '20px 0 10px';
        reportContent.appendChild(purchaseHeader);
        
        data.report.forEach(item => {
            if(item.medicine) {
                const div = document.createElement('div');
                div.className = 'order-item';
                div.innerHTML = `
                    <strong>${item.medicine}</strong><br>
                    <span style="color: green">✔ Bought from ${item.bought_from}</span><br>
                    <small>Price: ₹${item.price} | Delivery: ${item.delivery_days} days</small>
                `;
                reportContent.appendChild(div);
            }
        });
    }
    
    // Fallback if no data
    if (reportContent.innerHTML === '') {
        reportContent.innerHTML = '<p>No prescription data found.</p>';
    }

    // C. Raw Data for Debugging
    document.getElementById('rawData').textContent = JSON.stringify(data, null, 2);
}

// Toggle Raw Data
document.getElementById('toggleRaw').addEventListener('click', () => {
    document.getElementById('rawData').classList.toggle('hidden');
});