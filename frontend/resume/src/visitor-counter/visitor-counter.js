document.addEventListener("DOMContentLoaded", function() {
    fetch('https://func-crc-prod-001.azurewebsites.net/api/visitor_counter')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const element = document.querySelector('#visitor-counter');
            if (element && data.visitor_counter !== undefined) {
                element.innerText = data.visitor_counter;
            }
        })
        .catch(error => console.error('Error fetching visitor counter:', error));
});
