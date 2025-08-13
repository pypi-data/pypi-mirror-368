// Dashboard functionality for PlixLab - Storage-based metadata
class PresentationDashboard {
    constructor() {
        this.presentations = [];
        this.userId = null;
        this.init();
    }

    init() {
        // Direct Firebase auth approach - more reliable for dashboard
        const waitForFirebase = () => {
            if (typeof firebase !== 'undefined' && firebase.auth) {
                firebase.auth().onAuthStateChanged((user) => {
                    if (user) {
                        this.userId = user.uid;
                        console.log('Dashboard: User ID:', this.userId);
                        // Add a small delay to ensure Firebase Storage is ready
                        setTimeout(() => {
                            this.loadPresentations();
                        }, 500);
                    } else {
                        console.log('Dashboard: No user authenticated, redirecting to home');
                        window.location.href = '/';
                    }
                });
            } else {
                setTimeout(waitForFirebase, 500);
            }
        };
        
        waitForFirebase();
    }

    async loadPresentations() {
        try {
            this.showLoading();

            // Try to load from Firebase Storage metadata files
            if (typeof firebase !== 'undefined' && firebase.storage) {
                const storage = firebase.storage();
                
                // Configure storage emulator only in development
                if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
                    try {
                        storage.useEmulator('127.0.0.1', 9199);
                    } catch (e) {
                        // Storage emulator already configured or not needed
                    }
                }
                
                const userRef = storage.ref(`users/${this.userId}`);
                
                try {
                    // List all files in user's folder
                    console.log('Dashboard: Loading presentations from:', `users/${this.userId}`);
                    const listResult = await userRef.listAll();
                    console.log('Dashboard: Found', listResult.items.length, 'total files');
                    const presentations = [];
                    
                    // Filter for presentation files (not .metadata files)
                    const presentationFiles = listResult.items.filter(item => 
                        !item.name.endsWith('.metadata')
                    );
                    console.log('Dashboard: Found', presentationFiles.length, 'presentation files');
                    
                    for (const presentationFile of presentationFiles) {
                        try {
                            console.log('Dashboard: Processing file:', presentationFile.name);
                            // Get file metadata which includes our custom metadata
                            const metadata = await presentationFile.getMetadata();
                            console.log('Dashboard: Metadata for', presentationFile.name, ':', metadata);
                            
                            // Check if title exists in metadata
                            if (!metadata.customMetadata?.title) {
                                console.warn(`No title found in metadata for ${presentationFile.name}`);
                                // Use filename as fallback title
                                const title = `Presentation ${presentationFile.name.substring(0, 8)}`;
                                presentations.push({
                                    id: presentationFile.name,
                                    title: title,
                                    filePath: presentationFile.fullPath,
                                    fileRef: presentationFile,
                                    createdAt: metadata.timeCreated || new Date().toISOString(),
                                    url: `/share/${this.userId}/${presentationFile.name}`
                                });
                                continue;
                            }

                            const title = metadata.customMetadata.title;

                            // Add presentation data
                            const hash = presentationFile.name;
                            presentations.push({
                                id: hash,
                                title: title,
                                filePath: presentationFile.fullPath,
                                fileRef: presentationFile,
                                createdAt: metadata.timeCreated || new Date().toISOString(),
                                url: `/share/${this.userId}/${hash}`
                            });
                        } catch (error) {
                            console.warn('Failed to load metadata for:', presentationFile.name, error);
                        }
                    }
                    
                    // Sort by creation date (newest first)
                    this.presentations = presentations.sort((a, b) => 
                        new Date(b.createdAt) - new Date(a.createdAt)
                    );
                    
                    console.log('Dashboard: Final presentations list:', this.presentations);
                    this.renderPresentations();
                } catch (error) {
                    console.error('Storage access failed:', error);
                    this.showError();
                }
            } else {
                // Firebase not available
                this.showError();
            }
        } catch (error) {
            console.error('Error loading presentations:', error);
            this.showError();
        }
    }

    showLoading() {
        document.getElementById('presentations-loading').style.display = 'block';
        document.getElementById('presentations-list').style.display = 'none';
        document.getElementById('presentations-empty').style.display = 'none';
        document.getElementById('presentations-error').style.display = 'none';
    }

    showError() {
        document.getElementById('presentations-loading').style.display = 'none';
        document.getElementById('presentations-list').style.display = 'none';
        document.getElementById('presentations-empty').style.display = 'none';
        document.getElementById('presentations-error').style.display = 'block';
    }

    renderPresentations() {
        const loadingEl = document.getElementById('presentations-loading');
        const listEl = document.getElementById('presentations-list');
        const emptyEl = document.getElementById('presentations-empty');

        loadingEl.style.display = 'none';

        if (this.presentations.length === 0) {
            emptyEl.style.display = 'block';
            listEl.style.display = 'none';
            return;
        }

        emptyEl.style.display = 'none';
        listEl.style.display = 'block';

        listEl.innerHTML = this.presentations.map((presentation, index) => {
            return `
                <div class="presentation-item">
                    <a href="${presentation.url}" target="_blank" class="presentation-title">
                        ${presentation.title}
                    </a>
                    <button class="delete-btn" onclick="dashboard.deletePresentation(${index})" title="Delete presentation">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        }).join('');
    }

    getTypeIcon(type) {
        const icons = {
            'matplotlib': 'fas fa-chart-line',
            'plotly': 'fas fa-chart-bar',
            'bokeh': 'fas fa-chart-area',
            'default': 'fas fa-presentation'
        };
        return icons[type] || icons.default;
    }

    async savePresentationMetadata(presentationData) {
        try {
            if (typeof firebase !== 'undefined' && firebase.firestore && this.userId) {
                const db = firebase.firestore();
                await db.collection('presentations').add({
                    ...presentationData,
                    userId: this.userId,
                    createdAt: new Date()
                });
                console.log('Presentation metadata saved');
                this.loadPresentations(); // Refresh the list
            }
        } catch (error) {
            console.error('Error saving presentation metadata:', error);
        }
    }

    async deletePresentation(presentationIndex) {
        const presentation = this.presentations[presentationIndex];
        
        if (!presentation) {
            alert('Presentation not found.');
            return;
        }

        // Confirm deletion
        if (!confirm(`Are you sure you want to delete "${presentation.title}"? This action cannot be undone.`)) {
            return;
        }

        try {
            console.log('Deleting presentation:', presentation.title, 'at path:', presentation.filePath);
            
            // Delete the file using Firebase Storage
            if (presentation.fileRef) {
                await presentation.fileRef.delete();
                console.log('Presentation deleted successfully');
                
                // Refresh the presentations list
                this.loadPresentations();
            } else {
                throw new Error('File reference not available');
            }
            
        } catch (error) {
            console.error('Error deleting presentation:', error);
            
            // Show user-friendly error message
            let errorMessage = 'Failed to delete presentation. ';
            if (error.code === 'storage/unauthorized') {
                errorMessage += 'You do not have permission to delete this presentation.';
            } else if (error.code === 'storage/object-not-found') {
                errorMessage += 'Presentation not found.';
            } else {
                errorMessage += 'Please try again later.';
            }
            
            alert(errorMessage);
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for Firebase and other scripts to initialize
    setTimeout(() => {
        window.dashboard = new PresentationDashboard();
    }, 1000);
});
