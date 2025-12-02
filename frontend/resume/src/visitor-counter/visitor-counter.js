document.addEventListener("DOMContentLoaded", function() {
    fetch('https://webresume-to-counter.azurewebsites.net/api/webresume_to_counter?')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const element = document.querySelector('#visitor-counter');
            if (element && data.visits_counter !== undefined) {
                element.innerText = data.visits_counter;
            }
        })
        .catch(error => console.error('Error fetching visitor counter:', error));
});
