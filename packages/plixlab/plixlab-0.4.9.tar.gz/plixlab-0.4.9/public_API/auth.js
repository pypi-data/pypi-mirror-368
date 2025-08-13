// Unified PlixLab Authentication - Single source of truth
class PlixLabAuth {
    constructor() {
        this.currentUser = null;
        this.ui = null;
        this.isEmulator = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    }

    async init() {
        // Wait for Firebase to be ready
        return new Promise((resolve) => {
            const checkFirebase = () => {
                if (typeof firebase !== 'undefined' && firebase.auth) {
                    // Initialize FirebaseUI only if container exists
                    if (document.getElementById('firebaseui-auth-container')) {
                        this.ui = new firebaseui.auth.AuthUI(firebase.auth());
                    }
                    
                    // Set up auth state listener
                    firebase.auth().onAuthStateChanged((user) => {
                        this.currentUser = user;
                        this.handleAuthState(user);
                    });
                    resolve();
                } else {
                    setTimeout(checkFirebase, 100);
                }
            };
            checkFirebase();
        });
    }

    getUIConfig() {
        return {
            callbacks: {
                signInSuccessWithAuthResult: (authResult, redirectUrl) => {
                    // Silent redirect - no "redirecting" message
                    const currentPath = window.location.pathname;
                    let targetUrl = '/dashboard.html';
                    
                    if (this.isEmulator) {
                        targetUrl += '?useEmulator=true';
                    }
                    
                    // If we're already on dashboard, reload it
                    if (currentPath.includes('dashboard')) {
                        window.location.reload();
                    } else {
                        window.location.replace(targetUrl);
                    }
                    
                    return false; // Prevent FirebaseUI from handling redirect
                },
                uiShown: () => {
                    const loader = document.getElementById('loader');
                    if (loader) loader.style.display = 'none';
                }
            },
            signInFlow: 'popup',
            signInOptions: [
                {
                    provider: firebase.auth.GoogleAuthProvider.PROVIDER_ID,
                    customParameters: {
                        prompt: 'select_account'
                    }
                },
                firebase.auth.EmailAuthProvider.PROVIDER_ID,
            ]
        };
    }

    startSignIn(containerId = '#firebaseui-auth-container') {
        if (this.ui) {
            this.ui.start(containerId, this.getUIConfig());
        }
    }

    async signOut() {
        try {
            await firebase.auth().signOut();
            this.currentUser = null;
            
            // For emulator, clear browser storage for fresh sign-in
            if (this.isEmulator) {
                try {
                    // Only clear Firebase-specific keys, not everything
                    const firebaseKeys = [];
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        if (key && key.includes('firebase')) {
                            firebaseKeys.push(key);
                        }
                    }
                    firebaseKeys.forEach(key => localStorage.removeItem(key));
                } catch (e) {
                    console.log('Could not clear storage:', e);
                }
            }
            
            return true;
        } catch (error) {
            console.error('Sign out error:', error);
            return false;
        }
    }

    handleAuthState(user) {
        const signedInDiv = document.getElementById('signed-in');
        const notSignedInDiv = document.getElementById('not-signed-in');
        const userGreeting = document.getElementById('user-greeting');
        const loader = document.getElementById('loader');

        if (loader) loader.style.display = 'none';

        // Handle redirects silently
        const currentPath = window.location.pathname;
        
        if (user) {
            // User is authenticated
            if (currentPath === '/' || currentPath.includes('signin')) {
                // On landing/signin pages with authenticated user - silent redirect to dashboard
                if (currentPath.includes('signin')) {
                    window.location.replace('/dashboard.html');
                    return;
                }
            }
            
            // Show authenticated UI
            if (notSignedInDiv) notSignedInDiv.style.display = 'none';
            if (signedInDiv) {
                signedInDiv.style.display = 'block';
                if (userGreeting) {
                    userGreeting.textContent = `Welcome, ${user.displayName || user.email}!`;
                }
            }
        } else {
            // User not authenticated
            if (currentPath.includes('dashboard')) {
                // Protected page - redirect to signin
                window.location.replace('/signin.html');
                return;
            }
            
            // Show sign-in UI
            if (signedInDiv) signedInDiv.style.display = 'none';
            if (notSignedInDiv) notSignedInDiv.style.display = 'block';
            
            // Auto-start sign-in UI if container exists and not authenticated
            if (this.ui && document.getElementById('firebaseui-auth-container')) {
                this.startSignIn();
            }
        }
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isAuthenticated() {
        return this.currentUser !== null;
    }
}

// Global instance - single source of truth
window.plixAuth = new PlixLabAuth();

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.plixAuth.init().then(() => {
        // Set up all sign out buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#signOutBtn, .sign-out-btn, [id*="signOut"]')) {
                e.preventDefault();
                window.plixAuth.signOut();
            }
        });

        // Set up all token buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#token, .token-btn, [id*="token"]')) {
                e.preventDefault();
                const user = window.plixAuth.getCurrentUser();
                if (user) {
                    const display = document.getElementById('refreshTokenDisplay');
                    if (display) {
                        display.textContent = user.refreshToken || 'No refresh token available';
                        const modal = document.getElementById('tokenModal');
                        if (modal && typeof $ !== 'undefined') {
                            $('#tokenModal').modal('show');
                        }
                    }
                }
            }
        });
    });
});
