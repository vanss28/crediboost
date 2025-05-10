chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Message received in background:", message);
  
    if (message.action === 'fetch_url_and_classify') {
      // Query the active tab to get the URL
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0]?.url;  // Access URL of the active tab
  
        console.log("Active tab URL:", url);
  
        if (!url) {
          console.error('URL is undefined!');
          sendResponse({ error: 'URL not found' });
          return;
        }
  
        // Send URL to Flask backend
        fetch('http://127.0.0.1:5050/classify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        })
        .then(res => res.json())
        .then(data => {
          console.log("Received response from Flask:", data);
          sendResponse(data);  // Send the data back to popup.js
        })
        .catch(err => {
          console.error('API error:', err);
          sendResponse({ error: 'Failed to fetch data from backend' });
        });
      });
  
      // Return true to indicate the response is asynchronous
      return true;
    }
  });
  