document.addEventListener("DOMContentLoaded", function() {
    fetch('https://func-crc-prod-001.azurewebsites.net/api/visitor_counter')
        .then(async response => {
            const contentType = response.headers.get('content-type') || '';
            const rawText = await response.text();
            let data = null;

            if (contentType.includes('application/json')) {
                try {
                    data = JSON.parse(rawText);
                } catch (err) {
                    // Ignore parse errors and fall back to text if JSON isn't valid
                }
            } 

            if (!response.ok) {
                const errorDetail = data && data.message ? data.message : rawText;
                throw new Error(`HTTP error! status: ${response.status}. Detail: ${errorDetail}`);
            }

            return data;
        })    
        .then(data => {
            const element = document.querySelector('#visitor-counter');
            if (element && data && data.visitor_counter !== undefined) {
                element.innerText = data.visitor_counter;
            }
        })
        .catch(error => console.error('Error fetching visitor counter:', error));
});
