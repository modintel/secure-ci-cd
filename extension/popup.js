document.addEventListener('DOMContentLoaded', function () {
  checkCurrentTab();

  document.getElementById('checkBtn').addEventListener('click', function () {
    checkCurrentTab();
  });
});

function checkCurrentTab() {
  const statusDiv = document.getElementById('status');
  const urlDiv = document.getElementById('url');
  const detailsDiv = document.getElementById('details');

  statusDiv.textContent = "Scanning...";
  statusDiv.className = "status-text checking";

  detailsDiv.textContent = "--";

  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    if (!tabs || tabs.length === 0) return;

    const activeTab = tabs[0];
    const url = activeTab.url;

    urlDiv.textContent = url;

    const API_URL = 'https://127.0.0.1:5000/predict';
    fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: url })
    })
      .then(response => response.json())
      .then(data => {
        statusDiv.classList.remove('checking');

        if (data.error) {
          statusDiv.textContent = "Error";
          statusDiv.style.color = "#FF3B30"; // Red
          detailsDiv.textContent = "Server error";
          console.error(data.error);
        } else {
          if (data.result === "LEGITIMATE") {
            statusDiv.textContent = "Safe";
            statusDiv.classList.add("safe");
          } else {
            statusDiv.textContent = "Phishing";
            statusDiv.classList.add("phishing");
          }

          const percentage = (data.probability * 100).toFixed(1);
          detailsDiv.textContent = `${percentage}%`;
        }
      })
      .catch(error => {
        statusDiv.textContent = "Offline";
        statusDiv.classList.remove('checking');
        statusDiv.style.color = "#8E8E93";
        detailsDiv.textContent = "Is the server running?";
        console.error('Error:', error);
      });
  });
}
