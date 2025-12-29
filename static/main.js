let lastResult = null;

// Initialize visuals on load
document.addEventListener("DOMContentLoaded", () => {
    createSnowflakes();
});

function createSnowflakes() {
    const container = document.getElementById('snow-container');
    const snowflakeCount = 40; // Keeps it subtle

    for (let i = 0; i < snowflakeCount; i++) {
        const flake = document.createElement('div');
        flake.classList.add('snowflake');
        
        // Randomize size, position, and speed
        const size = Math.random() * 3 + 2 + 'px';
        flake.style.width = size;
        flake.style.height = size;
        flake.style.left = Math.random() * 100 + 'vw';
        flake.style.animationDuration = Math.random() * 10 + 5 + 's'; // 5-15s fall time
        flake.style.animationDelay = Math.random() * 5 + 's';
        
        container.appendChild(flake);
    }
}

async function startScrape() {
    const urlInput = document.getElementById("urlInput");
    const url = urlInput.value.trim();
    
    // UI Elements
    const status = document.getElementById("status-message");
    const loader = document.getElementById("loaderContainer");
    const sectionsDiv = document.getElementById("sections");
    const actionArea = document.getElementById("actionArea");
    const scrapeBtn = document.getElementById("scrapeBtn");

    if (!url) {
        status.textContent = "Please enter a valid URL";
        status.style.color = "#f87171"; // Red
        return;
    }

    // Reset UI State
    sectionsDiv.innerHTML = "";
    actionArea.style.display = "none";
    status.textContent = "Extracting data...";
    status.style.color = "#94a3b8"; // Default grey
    
    // Show loading
    loader.style.display = "block";
    scrapeBtn.disabled = true;
    urlInput.disabled = true;

    try {
        const response = await fetch("/scrape", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        lastResult = data;

        loader.style.display = "none";
        
        if (data.result && data.result.sections) {
            renderSections(data.result.sections);
            status.textContent = "Success! Download result for detailed view";
            status.style.color = "#4ade80"; // Green
            actionArea.style.display = "flex"; // Show download button
        } else {
            status.textContent = "No content sections found.";
            status.style.color = "#fbbf24"; // Yellow
        }
    } catch (err) {
        loader.style.display = "none";
        status.textContent = "Error: Could not scrape this URL.";
        status.style.color = "#f87171";
        console.error(err);
    } finally {
        scrapeBtn.disabled = false;
        urlInput.disabled = false;
    }
}

function renderSections(sections) {
    const container = document.getElementById("sections");
    container.innerHTML = "";

    sections.forEach(section => {
        const details = document.createElement("details");
        const summary = document.createElement("summary");

        summary.textContent = section.label || section.id || "Untitled Section";
        details.appendChild(summary);

        const pre = document.createElement("pre");
        pre.textContent = JSON.stringify(section, null, 2);
        details.appendChild(pre);

        container.appendChild(details);
    });
}

function downloadJSON() {
    if (!lastResult) return;

    const blob = new Blob(
        [JSON.stringify(lastResult, null, 2)],
        { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = "scrape-result.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}