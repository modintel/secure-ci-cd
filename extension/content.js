chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "SHOW_WARNING") {
        showWarningBanner();
    }
});

function showWarningBanner() {
    if (document.getElementById('phish-guard-warning')) return;

    const banner = document.createElement('div');
    banner.id = 'phish-guard-warning';
    banner.style.position = 'fixed';
    banner.style.top = '0';
    banner.style.left = '0';
    banner.style.width = '100%';
    banner.style.backgroundColor = '#FF3B30';
    banner.style.color = 'white';
    banner.style.textAlign = 'center';
    banner.style.padding = '15px';
    banner.style.fontSize = '18px';
    banner.style.fontWeight = 'bold';
    banner.style.zIndex = '999999';
    banner.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    banner.innerHTML = `
    ⚠️ WARNING: PHISHING DETECTED ⚠️
    <br>
    <span style="font-size: 14px; font-weight: normal;">This site has been identified as a potential phishing attempt. Do not enter any sensitive information.</span>
    <button id="phish-guard-close" style="margin-left: 20px; padding: 5px 10px; background: white; color: #FF3B30; border: none; border-radius: 4px; cursor: pointer;">Dismiss</button>
  `;

    document.body.prepend(banner);

    document.getElementById('phish-guard-close').addEventListener('click', () => {
        banner.remove();
    });
}
