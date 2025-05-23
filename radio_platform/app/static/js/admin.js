document.addEventListener('DOMContentLoaded', () => {
    const stationForm = document.getElementById('stationForm');
    const stationIdInput = document.getElementById('stationId');
    const nameInput = document.getElementById('name');
    const urlInput = document.getElementById('url');
    const genreInput = document.getElementById('genre');
    const descriptionInput = document.getElementById('description');
    const logoUrlInput = document.getElementById('logo_url');
    const stationList = document.getElementById('stationList');

    const apiBaseUrl = '/api/stations';

    // --- Main Functions ---

    async function fetchStations() {
        try {
            const response = await fetch(apiBaseUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const stations = await response.json();
            renderStationList(stations);
        } catch (error) {
            console.error('Error fetching stations:', error);
            stationList.innerHTML = '<p>Error loading stations. Check console for details.</p>';
        }
    }

    function renderStationList(stations) {
        stationList.innerHTML = ''; // Clear existing list

        if (stations.length === 0) {
            stationList.innerHTML = '<p>No stations found.</p>';
            return;
        }

        stations.forEach(station => {
            const item = document.createElement('div');
            item.classList.add('station-item'); // For potential styling
            item.innerHTML = `
                <h3>${station.name}</h3>
                <p><strong>URL:</strong> <a href="${station.url}" target="_blank">${station.url}</a></p>
                <p><strong>Genre:</strong> ${station.genre || 'N/A'}</p>
                <p><strong>Description:</strong> ${station.description || 'N/A'}</p>
                ${station.logo_url ? `<p><img src="${station.logo_url}" alt="${station.name} logo" style="max-width: 100px; max-height: 50px;"></p>` : ''}
                <button class="edit-btn" data-station-id="${station.id}">Edit</button>
                <button class="delete-btn" data-station-id="${station.id}">Delete</button>
            `;
            
            // Add event listeners to new buttons
            item.querySelector('.edit-btn').addEventListener('click', () => populateFormForEdit(station));
            item.querySelector('.delete-btn').addEventListener('click', () => deleteStation(station.id));
            
            stationList.appendChild(item);
        });
    }

    function populateFormForEdit(station) {
        stationIdInput.value = station.id;
        nameInput.value = station.name;
        urlInput.value = station.url;
        genreInput.value = station.genre || '';
        descriptionInput.value = station.description || '';
        logoUrlInput.value = station.logo_url || '';
        window.scrollTo(0, 0); // Scroll to top to see the form
    }

    async function handleFormSubmit(event) {
        event.preventDefault();

        const stationData = {
            name: nameInput.value,
            url: urlInput.value,
            genre: genreInput.value,
            description: descriptionInput.value,
            logo_url: logoUrlInput.value
        };

        const currentStationId = stationIdInput.value;
        let response;

        try {
            if (currentStationId) {
                // Update existing station (PUT)
                response = await fetch(`${apiBaseUrl}/${currentStationId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(stationData)
                });
            } else {
                // Create new station (POST)
                response = await fetch(apiBaseUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(stationData)
                });
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`API Error: ${errorData.error || response.statusText}`);
            }

            // const responseData = await response.json(); // Process if needed
            // console.log('Success:', responseData);

        } catch (error) {
            console.error('Error submitting form:', error);
            alert(`Error saving station: ${error.message}`); // Simple user feedback
        } finally {
            stationForm.reset();
            stationIdInput.value = ''; // Ensure hidden ID is cleared
            fetchStations(); // Refresh list
        }
    }

    async function deleteStation(id) {
        if (!confirm('Are you sure you want to delete this station?')) {
            return;
        }

        try {
            const response = await fetch(`${apiBaseUrl}/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`API Error: ${errorData.error || response.statusText}`);
            }
            // const responseData = await response.json(); // Process if needed
            // console.log('Deleted:', responseData);

        } catch (error) {
            console.error('Error deleting station:', error);
            alert(`Error deleting station: ${error.message}`); // Simple user feedback
        } finally {
            fetchStations(); // Refresh list regardless of form state
        }
    }

    // --- Event Listeners ---
    stationForm.addEventListener('submit', handleFormSubmit);

    // Initial load of stations
    fetchStations();
});
