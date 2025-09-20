// Loading state management utilities

const LoadingUtils = {
    // Active loading states
    activeLoaders: new Map(),

    // Loading overlay styles (injected once)
    injectStyles() {
        if (document.getElementById('loading-utils-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'loading-utils-styles';
        styles.textContent = `
            /* Loading overlay styles */
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                backdrop-filter: blur(2px);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .loading-overlay.active {
                opacity: 1;
            }

            .loading-container {
                background: white;
                border-radius: 12px;
                padding: 24px 32px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
                min-width: 200px;
            }

            /* Spinner animation */
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .loading-text {
                color: #333;
                font-size: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                text-align: center;
                margin: 0;
            }

            /* Inline loading indicator */
            .loading-inline {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: #f0f0f0;
                border-radius: 6px;
                font-size: 14px;
                color: #666;
            }

            .loading-inline-spinner {
                width: 16px;
                height: 16px;
                border: 2px solid #ddd;
                border-top: 2px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            /* Button loading state */
            .btn-loading {
                position: relative;
                pointer-events: none;
                opacity: 0.7;
            }

            .btn-loading::after {
                content: '';
                position: absolute;
                width: 16px;
                height: 16px;
                top: 50%;
                left: 50%;
                margin-left: -8px;
                margin-top: -8px;
                border: 2px solid #ffffff;
                border-top: 2px solid transparent;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            .btn-loading span {
                visibility: hidden;
            }

            /* Skeleton loader */
            .skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: 4px;
            }

            @keyframes shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }

            .skeleton-text {
                height: 16px;
                margin-bottom: 8px;
                border-radius: 4px;
            }

            .skeleton-title {
                height: 24px;
                width: 60%;
                margin-bottom: 16px;
                border-radius: 4px;
            }

            .skeleton-image {
                height: 200px;
                width: 100%;
                border-radius: 8px;
                margin-bottom: 16px;
            }

            .skeleton-button {
                height: 36px;
                width: 120px;
                border-radius: 6px;
            }

            /* Progress bar */
            .loading-progress {
                width: 100%;
                height: 4px;
                background: #f0f0f0;
                border-radius: 2px;
                overflow: hidden;
                margin-top: 12px;
            }

            .loading-progress-bar {
                height: 100%;
                background: #667eea;
                border-radius: 2px;
                transition: width 0.3s ease;
            }

            .loading-progress-text {
                font-size: 12px;
                color: #666;
                text-align: center;
                margin-top: 8px;
            }

            /* Dots animation */
            .loading-dots {
                display: inline-block;
            }

            .loading-dots::after {
                content: '';
                animation: dots 1.5s steps(4, end) infinite;
            }

            @keyframes dots {
                0% { content: ''; }
                25% { content: '.'; }
                50% { content: '..'; }
                75% { content: '...'; }
                100% { content: ''; }
            }
        `;
        document.head.appendChild(styles);
    },

    // Show full-screen loading overlay
    showOverlay(text = '\) ...', options = {}) {
        this.injectStyles();

        const id = options.id || 'default';

        // Remove existing overlay with same ID
        this.hideOverlay(id);

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = `loading-overlay-${id}`;

        const container = document.createElement('div');
        container.className = 'loading-container';

        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';

        const textEl = document.createElement('p');
        textEl.className = 'loading-text';
        textEl.innerHTML = text + '<span class="loading-dots"></span>';

        container.appendChild(spinner);
        container.appendChild(textEl);

        // Add progress bar if specified
        if (options.showProgress) {
            const progressContainer = document.createElement('div');
            progressContainer.className = 'loading-progress';
            progressContainer.style.width = '200px';

            const progressBar = document.createElement('div');
            progressBar.className = 'loading-progress-bar';
            progressBar.id = `progress-bar-${id}`;
            progressBar.style.width = '0%';

            progressContainer.appendChild(progressBar);
            container.appendChild(progressContainer);

            if (options.progressText) {
                const progressText = document.createElement('div');
                progressText.className = 'loading-progress-text';
                progressText.id = `progress-text-${id}`;
                progressText.textContent = '0%';
                container.appendChild(progressText);
            }
        }

        overlay.appendChild(container);
        document.body.appendChild(overlay);

        // Trigger animation
        setTimeout(() => overlay.classList.add('active'), 10);

        // Store reference
        this.activeLoaders.set(id, overlay);

        return id;
    },

    // Hide loading overlay
    hideOverlay(id = 'default') {
        const overlay = document.getElementById(`loading-overlay-${id}`);
        if (overlay) {
            overlay.classList.remove('active');
            setTimeout(() => overlay.remove(), 300);
            this.activeLoaders.delete(id);
        }
    },

    // Update progress
    updateProgress(id, percent, text = null) {
        const progressBar = document.getElementById(`progress-bar-${id}`);
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        const progressText = document.getElementById(`progress-text-${id}`);
        if (progressText) {
            progressText.textContent = text || `${percent}%`;
        }
    },

    // Show inline loading indicator
    showInline(containerId, text = '\) ...') {
        this.injectStyles();

        const container = document.getElementById(containerId);
        if (!container) return;

        const loading = document.createElement('div');
        loading.className = 'loading-inline';
        loading.id = `loading-inline-${containerId}`;

        const spinner = document.createElement('div');
        spinner.className = 'loading-inline-spinner';

        const textEl = document.createElement('span');
        textEl.textContent = text;

        loading.appendChild(spinner);
        loading.appendChild(textEl);

        // Store original content
        container.dataset.originalContent = container.innerHTML;
        container.innerHTML = '';
        container.appendChild(loading);
    },

    // Hide inline loading indicator
    hideInline(containerId, restoreContent = true) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const loading = document.getElementById(`loading-inline-${containerId}`);
        if (loading) {
            loading.remove();
        }

        if (restoreContent && container.dataset.originalContent) {
            container.innerHTML = container.dataset.originalContent;
            delete container.dataset.originalContent;
        }
    },

    // Add loading state to button
    setButtonLoading(button, loading = true, text = null) {
        this.injectStyles();

        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (!button) return;

        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.classList.add('btn-loading');
            if (text) {
                button.innerHTML = `<span>${text}</span>`;
            }
            button.disabled = true;
        } else {
            button.classList.remove('btn-loading');
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
                delete button.dataset.originalText;
            }
            button.disabled = false;
        }
    },

    // Create skeleton loader
    createSkeleton(type = 'text', count = 3) {
        this.injectStyles();

        const container = document.createElement('div');
        container.className = 'skeleton-container';

        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = `skeleton skeleton-${type}`;

            if (type === 'text') {
                skeleton.style.width = `${60 + Math.random() * 40}%`;
            }

            container.appendChild(skeleton);
        }

        return container;
    },

    // Replace element with skeleton
    showSkeleton(elementId, type = 'text', count = 3) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = '';
        element.appendChild(this.createSkeleton(type, count));
    },

    // Remove skeleton and restore content
    hideSkeleton(elementId, newContent = null) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const skeleton = element.querySelector('.skeleton-container');
        if (skeleton) {
            skeleton.remove();
        }

        if (newContent !== null) {
            element.innerHTML = newContent;
        } else if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
        }

        delete element.dataset.originalContent;
    },

    // Wrap async operation with loading state
    async withLoading(asyncFunc, options = {}) {
        const {
            text = '˜¬ ...',
            overlayId = 'default',
            showOverlay = true,
            buttonId = null,
            containerId = null,
            onError = null
        } = options;

        let loadingId = null;

        try {
            // Show loading state
            if (showOverlay) {
                loadingId = this.showOverlay(text, { id: overlayId });
            }
            if (buttonId) {
                this.setButtonLoading(buttonId, true, text);
            }
            if (containerId) {
                this.showInline(containerId, text);
            }

            // Execute async function
            const result = await asyncFunc();

            return result;
        } catch (error) {
            if (onError) {
                onError(error);
            } else {
                throw error;
            }
        } finally {
            // Hide loading state
            if (loadingId) {
                this.hideOverlay(loadingId);
            }
            if (buttonId) {
                this.setButtonLoading(buttonId, false);
            }
            if (containerId) {
                this.hideInline(containerId);
            }
        }
    },

    // Batch loading with progress
    async batchProcess(items, processor, options = {}) {
        const {
            batchSize = 10,
            text = '˜¬ ',
            showProgress = true
        } = options;

        const total = items.length;
        let processed = 0;

        const loadingId = this.showOverlay(text, {
            showProgress,
            progressText: showProgress
        });

        const results = [];

        try {
            for (let i = 0; i < total; i += batchSize) {
                const batch = items.slice(i, Math.min(i + batchSize, total));
                const batchResults = await Promise.all(
                    batch.map(item => processor(item))
                );

                results.push(...batchResults);
                processed += batch.length;

                const percent = Math.round((processed / total) * 100);
                this.updateProgress(loadingId, percent, `${processed} / ${total} DÌ`);
            }

            return results;
        } finally {
            this.hideOverlay(loadingId);
        }
    },

    // Lazy loading indicator for scroll
    observeLazyLoad(selector, callback) {
        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.01
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;

                    // Show loading state
                    this.showInline(element.id, '\) ...');

                    // Execute callback
                    callback(element).then(() => {
                        this.hideInline(element.id);
                        observer.unobserve(element);
                    });
                }
            });
        }, options);

        document.querySelectorAll(selector).forEach(el => {
            observer.observe(el);
        });

        return observer;
    }
};

// Make LoadingUtils available globally
window.LoadingUtils = LoadingUtils;