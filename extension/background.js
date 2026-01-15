import { WHITELIST } from './whitelist.js';

const API_URL = 'http://127.0.0.1:5000/predict';
const CACHE_DURATION = 24 * 60 * 60 * 1000;

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        handleUrlChange(tabId, tab.url);
    }
});

async function handleUrlChange(tabId, url) {
    if (!shouldScan(url)) {
        resetBadge(tabId);
        return;
    }

    const domain = getDomain(url);
    if (WHITELIST.has(domain)) {
        updateStatus(tabId, { result: 'LEGITIMATE', url: url }, true);
        return;
    }

    const cachedResult = await getFromCache(url);
    if (cachedResult) {
        updateStatus(tabId, cachedResult, true);
        return;
    }

    scanUrl(tabId, url);
}

function getDomain(url) {
    try {
        const hostname = new URL(url).hostname;
        return hostname.startsWith('www.') ? hostname : hostname;
    } catch {
        return '';
    }
}

function shouldScan(url) {
    if (!url || url.startsWith('chrome://') || url.startsWith('about:') || url.startsWith('chrome-extension://')) {
        return false;
    }
    return true;
}

function resetBadge(tabId) {
    chrome.action.setBadgeText({ text: '', tabId: tabId });
}

async function getFromCache(url) {
    const key = `scan_${url}`;
    const result = await chrome.storage.local.get(key);
    if (result[key]) {
        const data = result[key];
        if (Date.now() - data.timestamp < CACHE_DURATION) {
            return data.payload;
        } else {
            chrome.storage.local.remove(key);
        }
    }
    return null;
}

async function saveToCache(url, data) {
    const key = `scan_${url}`;
    await chrome.storage.local.set({
        [key]: {
            timestamp: Date.now(),
            payload: data
        }
    });
}

async function scanUrl(tabId, url) {
    chrome.action.setBadgeText({ text: '...', tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: '#FFA500', tabId: tabId });

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) throw new Error('API Error');

        const data = await response.json();

        saveToCache(url, data);

        updateStatus(tabId, data, false);

    } catch (error) {
        console.error('Scan error:', error);
        chrome.action.setBadgeText({ text: 'ERR', tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: '#8E8E93', tabId: tabId });
    }
}

function updateStatus(tabId, data, fromCache) {
    if (data.result === 'PHISHING') {
        chrome.action.setBadgeText({ text: 'DIE', tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: '#FF3B30', tabId: tabId });

        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'Phishing Detected!',
            message: `Warning: The site at ${data.url} appears to be a phishing site.${fromCache ? ' (Cached)' : ''}`,
            priority: 2
        });

        chrome.tabs.sendMessage(tabId, { action: "SHOW_WARNING" }).catch(() => { });

    } else {
        chrome.action.setBadgeText({ text: 'OK', tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: '#34C759', tabId: tabId });

        setTimeout(() => {
            chrome.action.setBadgeText({ text: '', tabId: tabId });
        }, 3000);
    }
}
