document.addEventListener('DOMContentLoaded', () => {
    fetchAndDisplayStations();
});

async function fetchAndDisplayStations() {
    const radioCardGrid = document.getElementById('radioCardGrid');
    const apiBaseUrl = '/api/stations'; // Assuming API is served from the same origin

    // Clear existing content (e.g., a "Loading..." message)
    radioCardGrid.innerHTML = '<p>Loading stations...</p>';

    try {
        const response = await fetch(apiBaseUrl);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API request failed with status ${response.status}: ${errorText}`);
        }

        const stations = await response.json();

        radioCardGrid.innerHTML = ''; // Clear "Loading..." message

        if (!stations || stations.length === 0) {
            radioCardGrid.innerHTML = '<p>No radio stations available at the moment.</p>';
            return;
        }

        stations.forEach(station => {
            const card = document.createElement('div');
            card.classList.add('radio-card');

            // Sanitize data before putting into innerHTML if it's user-generated
            // For this project, data comes from our admin-controlled DB, so direct insertion is acceptable.
            // However, for true user-generated content, use textContent for text and set attributes for URLs.

            const logoUrl = station.logo_url || 'https://via.placeholder.com/300x180.png?text=No+Logo'; // Updated placeholder

            card.innerHTML = `
                <img src="${logoUrl}" alt="${station.name || 'Station'} logo" class="card-logo">
                <div class="card-content">
                    <h3 class="card-name">${station.name || 'Unnamed Station'}</h3>
                    <p class="card-genre"><strong>Genre:</strong> ${station.genre || 'N/A'}</p>
                    <p class="card-description">${truncateDescription(station.description, 100)}</p>
                    <a href="${station.url}" target="_blank" class="card-listen-button">Listen Now</a>
                </div>
            `;
            // Note: The 'Listen Now' link directly uses station.url.
            // Ensure station.url is a valid stream URL or a page that leads to the stream.

            radioCardGrid.appendChild(card);
        });

    } catch (error) {
        console.error('Error fetching or displaying stations:', error);
        radioCardGrid.innerHTML = '<p>Could not load radio stations. Please try again later.</p>';
    }
}

function truncateDescription(description, maxLength) {
    if (!description) {
        return 'No description available.';
    }
    if (description.length <= maxLength) {
        return description;
    }
    return description.substring(0, maxLength) + '...';
}
