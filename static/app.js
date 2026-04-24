// Basic Vanilla JS App logic for AI Financial Dashboard

/**
 * Parses a CSV string to an array of objects.
 * Handles quoted fields containing commas.
 */
function parseCSV(csvText) {
  if (!csvText) return [];
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length < 2) return [];

  const headers = parseCSVLine(lines[0]);
  const data = [];

  for (let i = 1; i < lines.length; i++) {
    const rowStr = lines[i].trim();
    if (!rowStr) continue;
    const values = parseCSVLine(rowStr);
    const obj = {};
    headers.forEach((header, index) => {
      obj[header.trim()] = values[index] ? values[index].trim() : '';
    });
    data.push(obj);
  }
  return data;
}

/**
 * Regex approach to split CSV line handling quotes.
 */
function parseCSVLine(text) {
  const re_value = /(?!\s*$)\s*(?:'([^'\\]*(?:\\[\s\S][^'\\]*)*)'|"([^"\\]*(?:\\[\s\S][^"\\]*)*)"|([^,'"\s\\]*(?:\s+[^,'"\s\\]+)*))\s*(?:,|$)/g;
  let a = [];
  text.replace(re_value, function(m0, m1, m2, m3) {
      if      (m1 !== undefined) a.push(m1.replace(/\\'/g, "'"));
      else if (m2 !== undefined) a.push(m2.replace(/\\"/g, '"'));
      else if (m3 !== undefined) a.push(m3);
      return '';
  });
  // Handle empty trailing comma
  if (/,\s*$/.test(text)) a.push('');
  return a;
}

/**
 * Fetches and parses a CSV. Returns null if missing/error.
 */
async function fetchCSV(path) {
  try {
    const response = await fetch(path);
    if (!response.ok) {
      console.warn(`File ${path} not found or HTTP error. Status: ${response.status}`);
      return null;
    }
    const text = await response.text();
    return parseCSV(text);
  } catch (error) {
    console.error(`Error fetching CSV at ${path}:`, error);
    return null;
  }
}

/**
 * Fetches JSON payload.
 */
async function fetchJSON(path) {
  try {
    const response = await fetch(path);
    if (!response.ok) return null;
    return await response.json();
  } catch (e) {
    return null;
  }
}

/**
 * Retrieves a URL parameter by name
 */
function getQueryParam(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

/**
 * Handle navigation when a stock is selected from a dropdown 
 */
function handleStockSelection(elementId, targetPage, paramName = 'ticker') {
  const selectEl = document.getElementById(elementId);
  if (selectEl) {
    selectEl.addEventListener('change', (e) => {
      const ticker = e.target.value;
      if (ticker) {
        window.location.href = `${targetPage}?${paramName}=${ticker}`;
      }
    });
  }
}

/**
 * Generates an Empty State UI helper
 */
function generateEmptyState(message = 'Data currently unavailable') {
  return `
    <div class="empty-state animate-fade-in-up">
      <svg class="w-12 h-12 mb-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      <p class="text-sm font-medium">${message}</p>
    </div>
  `;
}

/**
 * Global fallback for graph images
 */
function handleImageError(imgObj, type = 'Graph') {
  imgObj.onerror = null; // prevent infinite loop
  imgObj.style.display = 'none';
  const parent = imgObj.parentElement;
  
  if (parent) {
    const emptyDiv = document.createElement('div');
    emptyDiv.innerHTML = generateEmptyState(`${type} Image Not Generated Yet`);
    emptyDiv.className = "w-full h-full flex items-center justify-center min-h-[200px]";
    parent.appendChild(emptyDiv);
  }
}

// Automatically bind the main navigation components if they exist
document.addEventListener('DOMContentLoaded', () => {
  handleStockSelection('main-stock-select', 'stock.html');
  
  const compareBtn = document.getElementById('compare-btn');
  if (compareBtn) {
    compareBtn.addEventListener('click', () => {
      const t1 = document.getElementById('compare-t1')?.value;
      const t2 = document.getElementById('compare-t2')?.value;
      if (t1 && t2) {
        if(t1 === t2) {
          alert('Please select two different stocks to compare.');
          return;
        }
        window.location.href = `compare.html?t1=${t1}&t2=${t2}`;
      } else {
        alert('Please select both stocks to compare.');
      }
    });
  }
});
