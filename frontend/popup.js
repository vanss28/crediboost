document.addEventListener('DOMContentLoaded', () => {
  console.log("Popup loaded");

  document.querySelectorAll('.close-btn').forEach(btn => {
    btn.addEventListener('click', () => window.close());
  });

  document.getElementById('detailsLink').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('summaryView').classList.add('hidden');
    document.getElementById('detailsView').classList.remove('hidden');
  });

  // Log message to confirm the sequence
  console.log("Sending message to background script");

  // Send message to background script to fetch URL and send to Flask
  chrome.runtime.sendMessage({ action: 'fetch_url_and_classify' }, (data) => {
    console.log("Received response from background script:", data);
    if (data) {
      if (data.error) {
        console.error(data.error);
      } else {
        const impact = data.impact_analysis;
        updateSummary(impact.avg_impact);
        updateDetails(impact);
      }
    }
  });
  
});


// Update summary view
function updateSummary(avgImpact) {
  const percentElem = document.querySelector('#summaryView .percent');
  percentElem.textContent = `${avgImpact.toFixed(1)}%`;

  const arrowElem = document.querySelector('#summaryView .arrow');
  const highlight = document.querySelector('#summaryView .highlight');

  if (avgImpact > 0) {
    arrowElem.textContent = '↑';
    highlight.classList.remove('green');
    highlight.classList.add('red');
  } else {
    arrowElem.textContent = '↓';
    highlight.classList.remove('red');
    highlight.classList.add('green');
  }
}

// Update detailed view
{/* <p><strong>Total reviews analyzed</strong></p>
<p class="gray-number">${data.total_reviews}</p>

<p><strong>Real reviews</strong></p>
<p class="gray-number">${data.real_reviews}</p>

<p><strong>Fake reviews</strong></p>
<p class="gray-number">${data.fake_reviews}</p>

<p><strong>Fake reviews with non-zero impact</strong></p>
<p class="gray-number">${data.nonzero_count}</p> */}

function updateDetails(data) {
  const detailsView = document.getElementById('detailsView');
  const percentageNonZero = data.fake_reviews > 0
  ? ((data.nonzero_count / data.fake_reviews) * 100).toFixed(1)
  : "0.0";
  detailsView.innerHTML = `
    <button class="close-btn">&times;</button>
    
   

    <p><strong>Percentage of fake reviews with non-zero impact</strong></p>
    <p class="gray-number">${percentageNonZero}%</p>

    <p><strong>Average impact of fake reviews</strong></p>
    <div class="highlight ${data.avg_impact > 0 ? 'red' : 'green'}">
      <span class="percent">${data.avg_impact.toFixed(1)}%</span>
      <span class="arrow">${data.avg_impact > 0 ? '↑' : '↓'}</span>
    </div>

    <p><strong>Median impact of fake reviews</strong></p>
    <p class="gray-number">${data.median_impact.toFixed(1)}%</p>

    <p><strong>Average impact (non-zero only)</strong></p>
    <p class="gray-number">${data.avg_impact_nonzero.toFixed(1)}%</p>

    <p><strong>Median impact (non-zero only)</strong></p>
    <p class="gray-number">${data.median_impact_nonzero.toFixed(1)}%</p>
  `;

  // Re-attach close button handler since we rewrote HTML
  detailsView.querySelector('.close-btn').addEventListener('click', () => window.close());
}
