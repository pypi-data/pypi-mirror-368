import { render_slides } from './plixlab.js';
const storage = firebase.storage();

// Configure storage emulator if we're in development
if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
  console.log('Using Firebase Storage emulator');
  storage.useEmulator('127.0.0.1', 9199);
}

window.addEventListener('DOMContentLoaded', async function () {
  console.log('DOM fully loaded and parsed');

  const loadingContainer = document.getElementById('loading-container');
  const loadingBar = document.getElementById('loading-bar');

  function showLoadingBar() {
    if (loadingBar && loadingContainer) {
      loadingBar.value = 0;
      loadingContainer.style.display = 'flex';
    }
  }

  function hideLoadingBar() {
    if (loadingContainer) {
      loadingContainer.style.display = 'none';
    }
  }

  function showError(message) {
    hideLoadingBar();
    // Create or update error display
    let errorDiv = document.getElementById('error-message');
    if (!errorDiv) {
      errorDiv = document.createElement('div');
      errorDiv.id = 'error-message';
      errorDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #f8d7da;
        color: #721c24;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        z-index: 1000;
      `;
      document.body.appendChild(errorDiv);
    }
    errorDiv.innerHTML = `
      <h3>Loading Error</h3>
      <p>${message}</p>
      <button onclick="location.reload()">Retry</button>
    `;
  }

  function updateLoadingBar(progress) {
    loadingBar.value = progress;
  }

  function extractPathFromURL() {
    // Get the full path after the domain
    const path = window.location.pathname;
    
    // Extract everything after the last slash
    const urlPart = path.substring(path.lastIndexOf('/') + 1);
    
    // Check if it contains a slash (uid/resourceId format)
    if (urlPart.includes('/')) {
      return urlPart;
    }
    
    // Fallback: check if the path itself contains the uid/resourceId
    // Remove leading slash and check if it's in format uid/resourceId
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    if (cleanPath.includes('/') && cleanPath.split('/').length >= 2) {
      const parts = cleanPath.split('/');
      // Take the last two parts as uid/resourceId
      return `${parts[parts.length - 2]}/${parts[parts.length - 1]}`;
    }
    
    // Fallback to query parameter (for compatibility)
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get('id');
    
    if (fromQuery) {
      return fromQuery;
    }

    console.error('Invalid URL format. Expected uid/resourceId format.');
    return null;
  }

  try {
    const resourcePath = extractPathFromURL();
    if (!resourcePath) return;

    // Parse the uid/resourceId format
    const parts = resourcePath.split('/');
    if (parts.length < 2) {
      showError('Invalid URL format. Expected uid/resourceId.');
      return;
    }
    
    const uid = parts[0];
    const resourceId = parts[1];
    const storagePath = `users/${uid}/${resourceId}`;
    
    console.log('Resource path:', resourcePath);
    console.log('Extracted UID:', uid);
    console.log('Extracted resource ID:', resourceId);
    console.log('Loading from Firebase Storage:', storagePath);

    showLoadingBar();

    const fileRef = storage.ref(storagePath);
    
    try {
      // Get download URL and fetch with proper CORS handling
      const downloadURL = await fileRef.getDownloadURL();
      
      // Use fetch API instead of XMLHttpRequest
      const response = await fetch(downloadURL);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const arrayBuffer = await response.arrayBuffer();
      
      hideLoadingBar();
      
      // Decode the MessagePack data
      const jsonData = msgpack.decode(new Uint8Array(arrayBuffer));
      
      // Check if slides are directly in jsonData or nested
      const slidesData = jsonData['slides'] || jsonData;
      
      render_slides(slidesData);
      
    } catch (error) {
      showError(`Failed to load presentation: ${error.message}`);
      console.error('Error loading presentation:', error.message);
    }
  } catch (err) {
    showError(`Invalid presentation URL or file not found`);
    console.error('Error loading presentation:', err.message);
  }
});

