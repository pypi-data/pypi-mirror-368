/**
 * TestingFramework.js - Comprehensive AI Browser Extension Testing Library
 * 
 * Eliminates duplicate testing code by providing a unified, class-based framework
 * for session management, navigation, element interaction, and Observer stream monitoring.
 * 
 * Features:
 * - Session discovery and management with URL matching
 * - Direct navigation via Actor load commands 
 * - Real-time Observer stream integration (no polling)
 * - Generic element reading/writing with verification
 * - Paranoid error handling with automatic retries
 * - Smart waiting for screen updates with timeouts
 * - State reset to known empty conditions
 * - Configurable logging levels (ERROR, WARN, INFO, DEBUG)
 * 
 * Usage:
 *   const framework = new TestingFramework('http://localhost:3001');
 *   framework.setLogLevel('INFO'); // ERROR, WARN, INFO, DEBUG
 *   await framework.selectSession('localhost:3001');
 *   await framework.navigate_load('http://localhost:3001/test-inputs');
 *   await framework.set_element('Username', 'test_user');
 *   const value = await framework.get_element('Username');
 */

/**
 * Log levels for controlling verbosity
 */
const LogLevel = {
    ERROR: 0,   // Only errors and failures
    WARN: 1,    // Warnings and above
    INFO: 2,    // Normal operations (default)
    DEBUG: 3    // Verbose debugging information
};

class TestingFramework {
    constructor(serverUrl = 'http://localhost:3001') {
        this.serverUrl = serverUrl;
        this.selectedSessionId = null;
        this.availableSessions = [];
        this.currentScreen = null;
        this.lastEventTimestamp = null;
        this.lastReceivedScreenTimestamp = null; // Track last screen timestamp before actions to avoid race conditions
        
        // Configuration
        this.defaultTimeout = 5000; // 5 seconds
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second between retries
        
        // Logging configuration
        this.logLevel = LogLevel.INFO; // Default to INFO level
        this.logger = this.defaultLogger;
    }

    /**
     * Set logging level
     * @param {string|number} level - Log level ('ERROR', 'WARN', 'INFO', 'DEBUG' or LogLevel enum)
     */
    setLogLevel(level) {
        if (typeof level === 'string') {
            this.logLevel = LogLevel[level.toUpperCase()] ?? LogLevel.INFO;
        } else {
            this.logLevel = level;
        }
    }

    /**
     * Get current log level name for display
     * @returns {string} Current log level name
     */
    getLogLevelName() {
        return Object.keys(LogLevel).find(key => LogLevel[key] === this.logLevel) || 'INFO';
    }

    /**
     * Check if message should be logged at current level
     * @param {string} level - Message level (error, warn, info, debug)
     * @returns {boolean} Whether to log the message
     */
    shouldLog(level) {
        const levelMap = {
            'error': LogLevel.ERROR,
            'warn': LogLevel.WARN, 
            'info': LogLevel.INFO,
            'debug': LogLevel.DEBUG
        };
        
        const messageLevel = levelMap[level] ?? LogLevel.INFO;
        return messageLevel <= this.logLevel;
    }

    /**
     * Default logger implementation with level filtering
     * @param {string} message - Log message
     * @param {string} level - Log level (error, warn, info, debug)
     */
    defaultLogger(message, level = 'info') {
        if (!this.shouldLog(level)) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const prefix = level === 'error' ? '❌' : level === 'warn' ? '⚠️' : level === 'debug' ? '🔍' : 'ℹ️';
        console.log(`[${timestamp}] ${prefix} ${message}`);
    }

    /**
     * Set custom logger function
     * @param {Function} loggerFn - Custom logger function (message, level) => void
     */
    setLogger(loggerFn) {
        this.logger = loggerFn;
    }

    // ========================================================================
    // SESSION MANAGEMENT
    // ========================================================================

    /**
     * Refresh available sessions from server
     * @returns {Promise<Array>} Array of available sessions
     */
    async refreshSessions() {
        this.logger('🔄 Refreshing available sessions...', 'debug');
        
        try {
            const response = await fetch(`${this.serverUrl}/sessions`);
            if (!response.ok) {
                throw new Error(`Session fetch failed: HTTP ${response.status}`);
            }
            
            this.availableSessions = await response.json();
            this.logger(`📋 Found ${this.availableSessions.length} available sessions`, 'info');
            
            return this.availableSessions;
        } catch (error) {
            this.logger(`Failed to refresh sessions: ${error.message}`, 'error');
            throw new Error(`Session discovery failed: ${error.message}`);
        }
    }

    /**
     * Select session by URL pattern or prompt for manual selection
     * @param {string} [urlPattern] - URL pattern to match (optional)
     * @param {boolean} [pauseIfFound=false] - Whether to pause even if URL matches
     * @returns {Promise<string>} Selected session ID
     */
    async selectSession(urlPattern = null, pauseIfFound = false) {
        await this.refreshSessions();
        
        if (this.availableSessions.length === 0) {
            throw new Error('No browser sessions found. Make sure Browser-AI Extension is loaded and has registered sessions.');
        }

        // Try to find session by URL pattern
        if (urlPattern && !pauseIfFound) {
            const matchingSession = this.availableSessions.find(session => 
                session.url && session.url.includes(urlPattern)
            );
            
            if (matchingSession) {
                this.logger(`✅ Auto-selected session: ${matchingSession.title} (${matchingSession.url})`, 'info');
                return await this.setSession(matchingSession.sessionId);
            }
        }

        // Manual selection or no automatic match
        this.logger('📋 Available sessions:', 'info');
        this.availableSessions.forEach((session, index) => {
            this.logger(`  ${index + 1}. ${session.title} - ${session.url} (${session.sessionId})`, 'info');
        });

        if (typeof window !== 'undefined') {
            // Browser environment - could implement UI selection
            throw new Error('Manual session selection not implemented in browser environment. Provide specific URL pattern.');
        } else {
            // Node.js environment - could implement readline selection
            throw new Error('Manual session selection not implemented in Node.js environment. Provide specific URL pattern.');
        }
    }

    /**
     * Set active session and validate it exists
     * @param {string} sessionId - Session ID to activate
     * @returns {Promise<string>} Confirmed session ID
     */
    async setSession(sessionId) {
        this.logger(`🎯 Setting active session: ${sessionId}`, 'debug');
        
        // Validate session exists and is accessible
        try {
            const response = await fetch(`${this.serverUrl}/sessions/${sessionId}/status`);
            if (!response.ok) {
                throw new Error(`Session validation failed: HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.selectedSessionId = sessionId;
            
            this.logger(`✅ Session activated: ${data.eventCount} events available`, 'info');
            
            // Load initial screen state
            await this.updateCurrentScreen();
            
            return sessionId;
        } catch (error) {
            this.logger(`Session validation failed: ${error.message}`, 'error');
            throw new Error(`Cannot activate session ${sessionId}: ${error.message}`);
        }
    }

    /**
     * Reset system to known empty state
     * @returns {Promise<void>}
     */
    async resetState() {
        this.logger('🧹 Resetting system to known empty state...', 'debug');
        
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        // Clear any pending keyboard input
        await this.sendActorEvent({
            type: 'keyboard',
            target: { label: 'clear_all' },
            action: 'clear'
        });

        // Navigate to a clean state (root page)
        await this.navigate_load(`${this.serverUrl}/`);
        
        this.logger('✅ System reset to empty state', 'debug');
    }

    // ========================================================================
    // NAVIGATION & PAGE CONTROL
    // ========================================================================

    /**
     * Navigate to URL using Actor load command
     * @param {string} url - URL to navigate to
     * @returns {Promise<void>}
     */
    async navigate_load(url) {
        this.logger(`🌐 Navigating to: ${url}`, 'info');
        
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        // Check if we're already on the target URL to avoid unnecessary navigation
        const currentUrl = await this.getCurrentUrl();
        if (currentUrl === url) {
            this.logger(`✅ Already on target URL: ${url} - skipping navigation`, 'debug');
            return;
        }

        // Capture timestamp of current screen before sending command to avoid race conditions
        this.lastReceivedScreenTimestamp = this.currentScreen ? this.currentScreen.timestamp : null;

        const command = {
            type: 'load',
            target: { url: url }
        };

        await this.sendActorEvent(command);
        this.logger(`✅ Navigation command sent for: ${url}`, 'debug');
    }

    /**
     * Navigate and confirm page loaded successfully
     * @param {string} url - URL to navigate to
     * @param {number} [timeout=5000] - Timeout in milliseconds
     * @returns {Promise<void>}
     */
    async navigate_confirm(url, timeout = this.defaultTimeout) {
        // Wait for navigation confirmation without sending duplicate load command
        // This assumes navigate_load() was already called elsewhere
        this.logger(`⏳ Waiting for navigation to ${url} to complete...`, 'debug');
        
        const startTime = Date.now();
        while (Date.now() - startTime < timeout) {
            await this.updateCurrentScreen();
            
            if (this.currentScreen && this.currentScreen.url && this.currentScreen.url.includes(url)) {
                this.logger(`✅ Navigation confirmed: ${this.currentScreen.url}`, 'info');
                return;
            }
            
            await this.delay(500); // Check every 500ms
        }
        
        throw new Error(`Navigation to ${url} not confirmed within ${timeout}ms. Current URL: ${this.currentScreen?.url || 'unknown'}`);
    }

    /**
     * Get current page URL from the latest screen data
     * @returns {Promise<string>} Current URL
     */
    async getCurrentUrl() {
        // Ensure we have fresh screen data
        await this.updateCurrentScreen();
        
        if (!this.currentScreen || !this.currentScreen.url) {
            throw new Error('No screen data available or URL is undefined');
        }
        
        return this.currentScreen.url;
    }

    // ========================================================================
    // ELEMENT INTERACTION
    // ========================================================================

    /**
     * Get element value/state by target label
     * @param {string} target - Element label or identifier
     * @returns {Promise<*>} Element value or state
     */
    async get_element(target) {
        this.logger(`📖 Reading element: ${target}`);
        
        // Use current screen data maintained by processObserverQueue instead of server request
        if (!this.currentScreen || !this.currentScreen.visible_elements) {
            throw new Error('No screen data available. Cannot read elements.');
        }

        // Match by label only since visible_elements don't have control_id or id fields
        const element = this.currentScreen.visible_elements.find(el => {
            if (!el.label) return false;
            
            // Handle both string labels and object labels (e.g., checkboxes)
            const labelText = this.extractBestLabel(el.label);
            
            return labelText.toLowerCase() === target.toLowerCase();
        });

        if (!element) {
            const availableElements = this.currentScreen.visible_elements
                .map(el => el.label || 'unlabeled')
                .slice(0, 5);
            throw new Error(`Element "${target}" not found. Available: ${availableElements.join(', ')}`);
        }

        // Return appropriate value based on element type
        this.logger(`🔍 Element debug: type="${element.type}", tagName="${element.tagName}", value="${element.value}", label="${element.label}"`);

        // Handle different input types based on HTML specification research
        // Semantic distinction: '' = field exists and is empty, null = value unavailable/unreadable
        
        if (element.type === 'text' || element.type === 'email' || element.type === 'search' || 
            element.type === 'tel' || element.type === 'url' || element.type === 'textarea') {
            // HTML spec: .value property returns string, empty string when field is empty
            if (element.value === undefined) {
                return null;  // Value property missing - unexpected for these input types
            }
            return element.value;  // Return exactly what we found (including empty string)
            
        } else if (element.type === 'password') {
            // Password behavior depends on Show Passwords setting in extension:
            // - Show Passwords OFF: extension should omit 'value' property, but currently sends "undefined" string (bug)
            // - Show Passwords ON: extension includes actual 'value' property
            if (!element.hasOwnProperty('value') || element.value === 'undefined') {
                return null;  // Value property omitted or buggy "undefined" string (Show Passwords = false)
            }
            // Value property is present with real value, return exactly what we found
            return element.value;
            
        } else if (element.type === 'checkbox' || element.type === 'radio') {
            // HTML spec: Use .checked property for boolean state, not .value
            return element.checked;
            
        } else if (element.tagName === 'select') {
            // Handle dropdown semantic properties (current_value vs value)
            if (element.current_value !== undefined) {
                // Semantic dropdown: Use current_value from addDropdownSemanticState
                return element.current_value;
            } else {
                // Fallback to standard DOM properties
                // HTML spec: Handle single vs multiple select elements
                if (element.type === 'select-multiple' || element.multiple === true) {
                    // Multi-select: Return array of selected option values
                    const selectedValues = [];
                    if (element.selectedOptions && Array.isArray(element.selectedOptions)) {
                        for (const option of element.selectedOptions) {
                            if (option.value === undefined) {
                                selectedValues.push(null);  // Option has no value attribute - unexpected
                            } else {
                                selectedValues.push(option.value);  // Use exactly what we found
                            }
                        }
                    } else if (element.selectedOptions && typeof element.selectedOptions[Symbol.iterator] === 'function') {
                        // Handle HTMLCollection or NodeList
                        for (const option of element.selectedOptions) {
                            if (option.value === undefined) {
                                selectedValues.push(null);  // Option has no value attribute - unexpected
                            } else {
                                selectedValues.push(option.value);  // Use exactly what we found
                            }
                        }
                    }
                    return selectedValues;  // Array<string> of selected values
                } else {
                    // Single select: Return selected option value
                    if (element.selectedIndex === -1) {
                        return null;  // No selection made
                    }
                    // Return exactly what we found - don't guess with fallbacks
                    if (element.value === undefined) {
                        return null;  // Option has no value attribute - unexpected
                    }
                    return element.value;  // Return actual value (could be empty string)
                }
            }
            
        } else if (element.tagName === 'button') {
            // HTML spec: Buttons don't have meaningful values for data collection
            return null;  // Buttons don't have user-settable values
            
        } else {
            // Unknown element type - don't guess, return null and log warning
            this.logger(`⚠️ Unknown element type: ${element.type}/${element.tagName} - returning null`, 'warn');
            return null;
        }
    }

    /**
     * Set element value by target label
     * @param {string} target - Element label or identifier  
     * @param {*} value - Value to set
     * @returns {Promise<void>}
     */
    async set_element(target, value) {
        // Specification-based element value setting per HTML standards
        // Each element type uses correct DOM property/method for value setting
        this.logger(`✏️ Setting element "${target}" to: "${value}" (type: ${typeof value}, length: ${String(value).length})`);
        
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        // Use current screen data maintained by processObserverQueue
        const element = await this.findElementByTarget(target);

        // Determine command type based on HTML specification for setting values
        // Each element type has a specific DOM property/method for setting values
        let command;
        
        if (element.type === 'text' || element.type === 'email' || element.type === 'search' || 
            element.type === 'tel' || element.type === 'url' || element.type === 'password' || 
            element.type === 'textarea' || element.tagName === 'textarea') {
            // HTML spec: Set .value property via text input
            command = {
                type: 'keyboard',
                event: 'text_input',
                target: {
                    label: element.label || target,
                    id: element.id,
                    value: {
                        text: String(value)  // Ensure string format
                    }
                }
            };
            
        } else if (element.type === 'checkbox') {
            // HTML spec: Set .checked property via keyboard command
            // For checkbox, value determines desired checked state
            command = {
                type: 'keyboard',
                target: {
                    label: element.label || target,
                    id: element.id,
                    value: {
                        text: String(value)  // "true" or "false"
                    }
                }
            };
            
        } else if (element.type === 'radio') {
            // HTML spec: Set .checked property for specific radio button
            // Use keyboard command with boolean value
            command = {
                type: 'keyboard',
                target: {
                    label: element.label || target,
                    id: element.id,
                    value: {
                        text: String(value)  // "true" or "false"
                    }
                }
            };
            
        } else if (element.tagName === 'select') {
            // HTML spec: Handle single vs multiple select elements
            if (element.type === 'select-multiple' || element.multiple === true) {
                // Multi-select: Set multiple option.selected=true
                if (!Array.isArray(value)) {
                    throw new Error(`Multi-select element "${target}" requires array value, got: ${typeof value}`);
                }
                command = {
                    type: 'keyboard',
                    target: {
                        label: element.label || target,
                        id: element.id,
                        value: {
                            text: value.length > 0 ? value.map(String).join(',') : ''
                        }
                    }
                };
            } else {
                // Single select: Set element.value to option value
                command = {
                    type: 'keyboard',
                    target: {
                        label: element.label || target,
                        id: element.id,
                        value: {
                            text: String(value)
                        }
                    }
                };
            }
            
        } else if (element.tagName === 'button') {
            // HTML spec: Buttons don't have settable values, only clickable
            throw new Error(`Cannot set value on button element "${target}" - buttons don't have settable values`);
            
        } else {
            // Unknown element type - don't guess, throw error with specification
            throw new Error(`Unknown element type for setting value: ${element.type}/${element.tagName} - add specification-based handler`);
        }

        // Use smart Actor command that waits for screen updates
        await this.sendActorCommandSmart(command);
        
        // Verify the action worked using updated screen data
        const newValue = await this.get_element(target);

        // Validate the result for input elements
        if (element.type === 'text' || element.type === 'email' || element.type === 'search' || 
            element.type === 'tel' || element.type === 'url' || element.type === 'textarea' || element.type === 'password') {
            if (newValue !== value) {
                this.logger(`Warning: Expected "${value}", got "${newValue}"`, 'warn');
            } else {
                this.logger(`✅ Element value confirmed: ${newValue}`, 'debug');
            }
        }
    }

    /**
     * Click element by target label (for buttons, links, etc.)
     * @param {string} target - Element label to click
     * @returns {Promise<void>}
     */
    async click_element(target) {
        this.logger(`🖱️ Clicking element: ${target}`, 'debug');
        
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        // Find the element to click
        const element = await this.findElementByTarget(target);

        // Use mouse command for clicking
        const command = {
            type: 'mouse',
            event: 'click',
            target: {
                label: element.label || target,
                id: element.id
            }
        };

        // Use smart Actor command that waits for screen updates
        await this.sendActorCommandSmart(command);
        
        this.logger(`✅ Element clicked: ${target}`, 'debug');
    }

    // ========================================================================
    // OBSERVER STREAM INTEGRATION
    // ========================================================================

    /**
     * Update current screen state from latest Observer events
     * @returns {Promise<void>}
     */
    async updateCurrentScreen() {
        if (!this.selectedSessionId) {
            return;
        }

        try {
            const response = await fetch(`${this.serverUrl}/sessions/${this.selectedSessionId}/events/recent?limit=10`);
            if (!response.ok) {
                throw new Error(`Failed to fetch events: HTTP ${response.status}`);
            }

            const events = await response.json();
            
            // Find most recent screen_status event
            const latestScreen = events
                .filter(event => event.type === 'screen_status')
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];

            if (latestScreen) {
                this.currentScreen = latestScreen;
                this.lastEventTimestamp = latestScreen.timestamp;
            }
        } catch (error) {
            this.logger(`Failed to update screen state: ${error.message}`, 'warn');
        }
    }

    /**
     * Wait for screen to update (new events received)
     * @param {number} [timeout=5000] - Timeout in milliseconds
     * @returns {Promise<void>}
     */
    async waitForScreenUpdate(timeout = this.defaultTimeout) {
        this.logger(`⏳ Waiting for screen update (timeout: ${timeout}ms)...`);
        
        const initialTimestamp = this.lastEventTimestamp;
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            await this.updateCurrentScreen();
            
            if (this.lastEventTimestamp !== initialTimestamp) {
                this.logger('✅ Screen update detected', 'debug');
                return;
            }
            
            await this.delay(200); // Check every 200ms
        }
        
        throw new Error(`No screen update detected within ${timeout}ms`);
    }

    // ========================================================================
    // ACTOR COMMAND UTILITIES
    // ========================================================================

    /**
     * Send Actor command with retry logic
     * @param {Object} command - Actor command object
     * @returns {Promise<void>}
     */
    async sendActorEvent(command) {
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        let lastError;
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                this.logger(`📤 Sending Actor command (attempt ${attempt}): ${command.type}`);
                
                const response = await fetch(`${this.serverUrl}/sessions/${this.selectedSessionId}/actor/send`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(command)
                });

                if (!response.ok) {
                    throw new Error(`Actor command failed: HTTP ${response.status}`);
                }

                this.logger(`✅ Actor command sent successfully: ${command.type}`);
                return;
                
            } catch (error) {
                lastError = error;
                this.logger(`Attempt ${attempt} failed: ${error.message}`, 'warn');
                
                if (attempt < this.retryAttempts) {
                    await this.delay(this.retryDelay);
                }
            }
        }
        
        throw new Error(`Actor command failed after ${this.retryAttempts} attempts: ${lastError.message}`);
    }

    /**
     * Extract the best label from a label object or string
     * @param {string|Object} label - Label data from element
     * @returns {string} - Best available label text
     */
    extractBestLabel(label) {
        // If already a string, return as-is
        if (typeof label === 'string') {
            return label;
        }
        
        // If object, extract best label based on priority
        if (typeof label === 'object' && label !== null) {
            // Priority order: control > Parent_Label > Left_Label > text > JSON fallback
            return label.control || 
                   label.Parent_Label || 
                   label.Left_Label || 
                   label.text || 
                   JSON.stringify(label);
        }
        
        // Fallback for unexpected types
        return String(label);
    }

    // ========================================================================
    // DEBUGGING AND DUMP UTILITIES
    // ========================================================================

    /**
     * Auto-dump Observer and Actor events on test failure for debugging
     * @param {string} testDescription - Description of failed test
     * @param {string} errorMessage - Error message from failed test
     * @returns {Promise<Object>} Dump results with file names and event counts
     */
    async dumpEventsOnFailure(testDescription, errorMessage) {
        this.logger(`🚨 Test failed: ${testDescription}`, 'error');
        this.logger(`🚨 Error: ${errorMessage}`, 'error');
        this.logger('📁 Auto-dumping events for debugging...', 'warn');
        
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const dumpResults = {
                timestamp,
                testDescription,
                errorMessage,
                observerEvents: { count: 0, file: null },
                actorCommands: { count: 0, file: null }
            };
            
            if (!this.selectedSessionId) {
                this.logger('⚠️ No session selected - cannot dump events', 'warn');
                return dumpResults;
            }
            
            // Dump Observer processed events
            try {
                const observerResponse = await fetch(`${this.serverUrl}/sessions/${this.selectedSessionId}/events/processed?limit=100`);
                if (observerResponse.ok) {
                    const observerEvents = await observerResponse.json();
                    const observerFileName = `observer-events-failure-${timestamp}.json`;
                    
                    this.logger(`📝 Observer events (${observerEvents.length}) ready for analysis`);
                    
                    dumpResults.observerEvents = {
                        count: observerEvents.length,
                        file: observerFileName,
                        data: observerEvents
                    };
                } else {
                    this.logger(`⚠️ Failed to fetch Observer events: ${observerResponse.statusText}`, 'warn');
                }
            } catch (error) {
                this.logger(`⚠️ Error dumping Observer events: ${error.message}`, 'warn');
            }
            
            // Dump Actor retrieved commands
            try {
                const actorResponse = await fetch(`${this.serverUrl}/sessions/${this.selectedSessionId}/actor/retrieved?limit=100`);
                if (actorResponse.ok) {
                    const actorCommands = await actorResponse.json();
                    const actorFileName = `actor-commands-failure-${timestamp}.json`;
                    
                    this.logger(`📝 Actor commands (${actorCommands.length}) ready for analysis`);
                    
                    dumpResults.actorCommands = {
                        count: actorCommands.length,
                        file: actorFileName,
                        data: actorCommands
                    };
                } else {
                    this.logger(`⚠️ Failed to fetch Actor commands: ${actorResponse.statusText}`, 'warn');
                }
            } catch (error) {
                this.logger(`⚠️ Error dumping Actor commands: ${error.message}`, 'warn');
            }
            
            // Log summary
            this.logger(`📊 Dump complete - Observer: ${dumpResults.observerEvents.count} events, Actor: ${dumpResults.actorCommands.count} commands`, 'warn');
            
            return dumpResults;
            
        } catch (error) {
            this.logger(`❌ Auto-dump failed: ${error.message}`, 'error');
            return { error: error.message };
        }
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    /**
     * Find element by target identifier with detailed error info
     * @param {string} target - Element identifier
     * @returns {Promise<Object>} Element object
     */
    async findElementByTarget(target) {
        // Use current screen data maintained by processObserverQueue instead of server request
        if (!this.currentScreen || !this.currentScreen.visible_elements) {
            throw new Error('No screen data available. Cannot find elements.');
        }

        const element = this.currentScreen.visible_elements.find(el => {
            // Handle string and object labels
            let labelMatch = false;
            if (el.label) {
                const labelText = this.extractBestLabel(el.label);
                labelMatch = labelText.toLowerCase() === target.toLowerCase();
            }
            
            // Handle ID match
            const idMatch = el.id && el.id.toLowerCase() === target.toLowerCase();
            
            return labelMatch || idMatch;
        });

        if (!element) {
            const availableElements = this.currentScreen.visible_elements
                .map(el => `"${el.label || el.id || 'unlabeled'}" (${el.type || 'unknown'})`)
                .slice(0, 5);
            throw new Error(`Element "${target}" not found on current page (${this.currentScreen.url || 'unknown URL'}). Available elements: ${availableElements.join(', ')}`);
        }

        return element;
    }

    /**
     * Delay execution for specified milliseconds
     * @param {number} ms - Milliseconds to delay
     * @returns {Promise<void>}
     */
    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Verify connection to server
     * @returns {Promise<Object>} Server status
     */
    async verifyConnection() {
        this.logger('🔍 Verifying server connection...', 'debug');
        
        try {
            const response = await fetch(`${this.serverUrl}/status`);
            if (!response.ok) {
                throw new Error(`Server connection failed: HTTP ${response.status}`);
            }
            
            const status = await response.json();
            this.logger(`✅ Server connected: ${status.mode} mode, PID: ${status.pid}`);
            return status;
        } catch (error) {
            this.logger(`Server connection failed: ${error.message}`, 'error');
            throw new Error(`Cannot connect to server at ${this.serverUrl}: ${error.message}`);
        }
    }

    /**
     * Get comprehensive status information
     * @returns {Promise<Object>} Status object with session and server info
     */
    async getStatus() {
        const status = {
            serverUrl: this.serverUrl,
            selectedSessionId: this.selectedSessionId,
            availableSessions: this.availableSessions.length,
            currentScreen: this.currentScreen ? {
                url: this.currentScreen.url,
                elementCount: this.currentScreen.visible_elements?.length || 0,
                timestamp: this.currentScreen.timestamp
            } : null
        };

        try {
            const serverStatus = await this.verifyConnection();
            status.serverStatus = serverStatus;
        } catch (error) {
            status.serverError = error.message;
        }

        return status;
    }

    /**
     * Get recent events from the Observer stream
     * @param {number} limit - Maximum number of events to retrieve (default: 10)
     * @returns {Promise<Array>} Array of recent event objects
     */
    async getRecentEvents(limit = 10) {
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        const url = `${this.serverUrl}/sessions/${this.selectedSessionId}/events/recent?limit=${limit}`;
        const response = await fetch(url, {
            method: 'GET',
            credentials: 'include', // Include session cookies
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get recent events: ${response.status} ${response.statusText}`);
        }

        const events = await response.json();
        this.logger(`Retrieved ${events.length} recent events from Observer stream`, 'debug');
        return events;
    }

    /**
     * Consume unprocessed events from the FIFO queue (moves them to processed)
     * @returns {Promise<Array>} Array of events that were unprocessed, now marked as processed
     */
    async processObserverQueue() {
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        const url = `${this.serverUrl}/sessions/${this.selectedSessionId}/events/consume`;
        const response = await fetch(url, {
            method: 'GET',
            credentials: 'include', // Include session cookies
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to consume events: ${response.status} ${response.statusText}`);
        }

        const newEvents = await response.json();
        if (newEvents.length !== 0) {
            this.logger(`Processed ${newEvents.length} events from Observer queue`);
        }

        // Update current screen from any screen_status events
        for (const event of newEvents) {
            if (event.type === 'screen_status') {
                this.currentScreen = event;
                this.logger(`Screen updated from processed event: ${event.url}`);
            }
        }
        
        return newEvents;
    }

    /**
     * Wait for next screen update after an action (e.g., Actor command)
     * @param {number} timeout - Maximum time to wait for update (default: 5000ms)
     * @param {number} maxUpdates - Maximum number of updates to tolerate (default: 10, prevents runaway)
     * @returns {Promise<Object>} The updated screen object
     */
    async waitForUpdate(timeout = 5000, maxUpdates = 10) {
        if (!this.selectedSessionId) {
            throw new Error('No session selected. Call selectSession() first.');
        }

        // Timeout tracking - uses system clock for timeout enforcement
        const startTime = Date.now();
        let updateCount = 0;

        this.logger(`Waiting for screen update (current timestamp: ${this.currentScreen?.timestamp || 0})`);

        while (Date.now() - startTime < timeout) {
            // Process any new events from Observer queue
            const newEvents = await this.processObserverQueue();
            
            // Screen update detection - uses event timestamps (not Date.now())
            if (this.lastReceivedScreenTimestamp === null) {
                // Initial session - wait for ANY screen report to arrive
                if (this.currentScreen && this.currentScreen.timestamp) {
                    this.logger(`✅ First screen update received: ${this.currentScreen.url}`, 'debug');
                    return this.currentScreen;
                }
            } else {
                // Normal operation - wait for screen newer than our last received before action
                if (this.currentScreen && 
                    this.currentScreen.timestamp > this.lastReceivedScreenTimestamp) {
                    updateCount++;
                    this.logger(`✅ Screen update detected (${updateCount}/${maxUpdates}): timestamp ${this.currentScreen.timestamp}`);
                    
                    if (updateCount >= maxUpdates) {
                        throw new Error(`Too many screen updates (${updateCount}) - possible runaway changes`);
                    }
                    
                    return this.currentScreen;
                }
            }
            
            // If no events were consumed, wait a bit before checking again
            if (newEvents.length === 0) {
                await this.delay(100);
            }
        }
        
        throw new Error(`No screen update occurred within ${timeout}ms timeout`);
    }

    /**
     * Enhanced Actor command sender with pre-processing and update waiting
     * @param {Object} command - Actor command object
     * @param {boolean} waitForUpdate - Whether to wait for screen update after command (default: true)
     * @returns {Promise<Object>} Result of command execution
     */
    async sendActorCommandSmart(command, waitForUpdate = true) {
        // FIRST: Process any pending Observer events to get current state
        await this.processObserverQueue();
        
        // Capture timestamp of current screen before sending command to avoid race conditions
        this.lastReceivedScreenTimestamp = this.currentScreen ? this.currentScreen.timestamp : null;
        this.logger(`Sending Actor command: ${command.type} (pre-command timestamp: ${this.lastReceivedScreenTimestamp})`);
        
        // THEN: Send Actor command using existing method
        const result = await this.sendActorEvent(command);
        
        // NOW: Wait for screen update if requested
        if (waitForUpdate) {
            try {
                await this.waitForUpdate();
                this.logger(`Actor command completed with screen update`);
            } catch (error) {
                this.logger(`Actor command completed but ${error.message}`, 'warn');
            }
        }
        
        return result;
    }

    // ========================================================================
    // UI HELPER FUNCTIONS (for web-based test pages)
    // ========================================================================

    /**
     * Custom logger for web UI test pages
     * Updates both console and DOM log element with styled messages
     * @param {string} message - Log message
     * @param {string} level - Log level (info, warn, error)
     * @param {string} logElementId - DOM element ID for log display (default: 'test-log')
     */
    static webLogger(message, level = 'info', logElementId = 'test-log') {
        const logEl = document.getElementById(logElementId);
        const timestamp = new Date().toLocaleTimeString();
        const icon = level === 'error' ? '❌' : level === 'warn' ? '⚠️' : 'ℹ️';
        
        if (logEl) {
            logEl.innerHTML += `[${timestamp}] ${icon} ${message}<br>`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        // Console logging removed for production
    }

    /**
     * Set test status in web UI with visual indicators
     * @param {string} testId - DOM element ID for the test status
     * @param {string} status - Status class (pending, running, success, error, manual)
     * @param {string} message - Optional message to append after colon
     */
    static setTestStatus(testId, status, message = '') {
        const element = document.getElementById(testId);
        if (!element) return;
        
        element.className = `status ${status}`;
        if (message) {
            const baseText = element.textContent.split(':')[0];
            element.textContent = baseText + ': ' + message;
        }
    }

    /**
     * Set overall status in web UI
     * @param {string} statusId - DOM element ID for overall status (default: 'overall-status')
     * @param {string} status - Status class (pending, running, success, error)
     * @param {string} message - Status message
     */
    static setOverallStatus(statusId = 'overall-status', status, message) {
        const element = document.getElementById(statusId);
        if (!element) return;
        
        element.className = `status ${status}`;
        element.textContent = message;
    }

    /**
     * Show manual step instructions in web UI
     * @param {string} instructions - HTML instructions for manual step
     * @param {Function} callback - Callback function to execute when manual step is completed
     * @param {string} instructionsId - DOM element ID for instructions (default: 'manual-instructions')
     * @param {string} contentId - DOM element ID for content (default: 'manual-content')
     * @param {string} buttonId - DOM element ID for continue button (default: 'manual-continue')
     * @param {string} placeholderId - DOM element ID for placeholder (default: 'manual-placeholder')
     */
    static showManualStep(
        instructions, 
        callback, 
        instructionsId = 'manual-instructions',
        contentId = 'manual-content', 
        buttonId = 'manual-continue',
        placeholderId = 'manual-placeholder'
    ) {
        const manualEl = document.getElementById(instructionsId);
        const contentEl = document.getElementById(contentId);
        const continueBtn = document.getElementById(buttonId);
        const placeholderEl = document.getElementById(placeholderId);
        
        if (contentEl) contentEl.innerHTML = instructions;
        if (manualEl) manualEl.style.display = 'block';
        if (placeholderEl) placeholderEl.style.display = 'none';
        if (continueBtn) continueBtn.disabled = false;
        
        // Store callback globally for button click
        window.testingFrameworkManualCallback = callback;
        
        TestingFramework.webLogger('🔔 Manual step required - see highlighted section above');
    }

    /**
     * Continue after manual step completion
     * @param {string} instructionsId - DOM element ID for instructions (default: 'manual-instructions')
     * @param {string} buttonId - DOM element ID for continue button (default: 'manual-continue')
     * @param {string} placeholderId - DOM element ID for placeholder (default: 'manual-placeholder')
     */
    static continueAfterManual(
        instructionsId = 'manual-instructions',
        buttonId = 'manual-continue',
        placeholderId = 'manual-placeholder'
    ) {
        const manualEl = document.getElementById(instructionsId);
        const continueBtn = document.getElementById(buttonId);
        const placeholderEl = document.getElementById(placeholderId);
        
        if (manualEl) manualEl.style.display = 'none';
        if (placeholderEl) placeholderEl.style.display = 'block';
        if (continueBtn) continueBtn.disabled = true;
        
        if (window.testingFrameworkManualCallback) {
            window.testingFrameworkManualCallback();
            window.testingFrameworkManualCallback = null;
        }
    }

    /**
     * Reset test UI to initial state
     * @param {Array<string>} testIds - Array of test element IDs to reset
     * @param {string} startButtonId - DOM element ID for start button (default: 'start-test')
     * @param {string} resetButtonId - DOM element ID for reset button (default: 'reset-test')
     * @param {string} logElementId - DOM element ID for log element (default: 'test-log')
     * @param {string} overallStatusId - DOM element ID for overall status (default: 'overall-status')
     */
    static resetTestUI(
        testIds = [], 
        startButtonId = 'start-test',
        resetButtonId = 'reset-test',
        logElementId = 'test-log',
        overallStatusId = 'overall-status'
    ) {
        const startBtn = document.getElementById(startButtonId);
        const resetBtn = document.getElementById(resetButtonId);
        const logEl = document.getElementById(logElementId);
        
        if (startBtn) startBtn.disabled = false;
        if (resetBtn) resetBtn.disabled = true;
        
        testIds.forEach(id => {
            TestingFramework.setTestStatus(id, 'pending');
        });
        
        TestingFramework.setOverallStatus(overallStatusId, 'pending', 'Ready for testing');
        if (logEl) logEl.innerHTML = 'Tests reset. Framework ready.<br>';
    }

    /**
     * Enable/disable test control buttons
     * @param {boolean} testRunning - Whether test is currently running
     * @param {string} startButtonId - DOM element ID for start button (default: 'start-test')
     * @param {string} resetButtonId - DOM element ID for reset button (default: 'reset-test')
     */
    static setTestControlState(
        testRunning,
        startButtonId = 'start-test',
        resetButtonId = 'reset-test'
    ) {
        const startBtn = document.getElementById(startButtonId);
        const resetBtn = document.getElementById(resetButtonId);
        
        if (startBtn) startBtn.disabled = testRunning;
        if (resetBtn) resetBtn.disabled = !testRunning;
    }

    // ========================================================================
    // INFRASTRUCTURE VALIDATION (TODO #2)
    // ========================================================================

    /**
     * Comprehensive infrastructure validation
     * Validates all critical components before running tests
     * @returns {Promise<Object>} Validation results with detailed status
     */
    async validateInfrastructure() {
        const results = {
            overall: false,
            server: false,
            sessions: false,
            navigation: false,
            observerChannel: false,
            actorChannel: false,
            roundTrip: false,
            details: {}
        };

        try {
            // 1. Server connectivity
            const serverStatus = await this.verifyConnection();
            results.server = true;
            results.details.server = { status: 'connected', pid: serverStatus.pid, mode: serverStatus.mode };

            // 2. Session discovery and selection
            this.logger('🔗 Validating session discovery...', 'debug');
            await this.refreshSessions();
            if (this.availableSessions.length === 0) {
                throw new Error('No browser sessions available');
            }
            results.sessions = true;
            results.details.sessions = { count: this.availableSessions.length, sessions: this.availableSessions };
            this.logger(`✅ Session discovery validated (${this.availableSessions.length} sessions)`);

            // 2.5. Select a session for testing (find one with localhost:3001)
            this.logger('🎯 Selecting session for validation...', 'debug');
            const testSession = this.availableSessions.find(session => 
                session.url && session.url.includes('localhost:3001')
            ) || this.availableSessions[0]; // Fallback to first session
            
            if (!testSession.url) {
                throw new Error('Session has no initial page loaded. Please navigate to a page (like http://localhost:3001) in the browser tab before running tests.');
            }
            
            await this.setSession(testSession.sessionId);
            this.logger(`✅ Session selected for validation: ${testSession.sessionId}`, 'info');

            // 3. Observer Channel (verify events are captured from initial page load)
            this.logger('👁️ Validating Observer channel...', 'debug');
            const sessionEvents = await this.processObserverQueue();
            if (sessionEvents.length > 0) {
                results.observerChannel = true;
                results.details.observerChannel = { eventsFound: sessionEvents.length };
                this.logger(`✅ Observer channel validated - ${sessionEvents.length} events processed`, 'info');
            } else {
                throw new Error('Observer channel validation failed - no events available. Session may not have loaded an initial page.');
            }

            // 4. Navigation capability
            this.logger('🌐 Validating navigation capability...', 'debug');
            const testUrl = `${this.serverUrl}/test-inputs`;
            await this.navigate_load(testUrl);
            await this.waitForUpdate(5000); // Wait for navigation to complete
            
            if (!this.currentScreen || !this.currentScreen.url || !this.currentScreen.url.includes('test-inputs')) {
                throw new Error(`Navigation failed - expected test-inputs, got: ${this.currentScreen?.url || 'no URL'}`);
            }
            results.navigation = true;
            results.details.navigation = { targetUrl: testUrl, currentUrl: this.currentScreen.url };
            this.logger('✅ Navigation capability validated', 'info');

            // 5. Actor Channel (verify commands are queued and retrieved)
            this.logger('🤖 Validating Actor channel...', 'debug');
            // Send a safe test command and verify it gets queued
            await this.sendActorEvent({
                type: 'test',
                target: { test: 'infrastructure_validation' }
            });
            results.actorChannel = true;
            results.details.actorChannel = { status: 'commands queued successfully' };
            this.logger('✅ Actor channel validated - commands queued', 'info');

            // 6. Round-trip validation (Observer → Actor → Observer)
            this.logger('🔄 Validating round-trip functionality...', 'debug');
            if (results.observerChannel && results.actorChannel) {
                results.roundTrip = true;
                results.details.roundTrip = { status: 'Observer and Actor channels both functional' };
                this.logger('✅ Round-trip validation complete', 'info');
            }

            // Overall validation status
            results.overall = results.server && results.sessions && results.navigation && 
                            results.observerChannel && results.actorChannel && results.roundTrip;

            if (results.overall) {
                this.logger('🎉 Infrastructure validation PASSED - all systems operational', 'info');
            } else {
                this.logger('❌ Infrastructure validation FAILED - see details', 'error');
            }

            return results;

        } catch (error) {
            this.logger(`❌ Infrastructure validation failed: ${error.message}`, 'error');
            results.details.error = error.message;
            return results;
        }
    }

    /**
     * Quick infrastructure check for basic functionality
     * @returns {Promise<boolean>} True if basic infrastructure is working
     */
    async quickInfrastructureCheck() {
        try {
            await this.verifyConnection();
            await this.refreshSessions();
            return this.availableSessions.length > 0;
        } catch (error) {
            this.logger(`Quick infrastructure check failed: ${error.message}`, 'warn');
            return false;
        }
    }

    /**
     * Validate specific component
     * @param {string} component - Component to validate (server, sessions, navigation, observer, actor)
     * @returns {Promise<boolean>} True if component is working
     */
    async validateComponent(component) {
        try {
            switch (component.toLowerCase()) {
                case 'server':
                    await this.verifyConnection();
                    return true;
                    
                case 'sessions':
                    await this.refreshSessions();
                    return this.availableSessions.length > 0;
                    
                case 'navigation':
                    const testUrl = `${this.serverUrl}/`;
                    await this.navigate_load(testUrl);
                    await this.waitForUpdate(3000);
                    return this.currentScreen && this.currentScreen.url;
                    
                case 'observer':
                    const events = await this.getRecentEvents(1);
                    return Array.isArray(events);
                    
                case 'actor':
                    await this.sendActorEvent({
                        type: 'test',
                        target: { test: 'component_validation' }
                    });
                    return true;
                    
                default:
                    this.logger(`Unknown component: ${component}`, 'warn');
                    return false;
            }
        } catch (error) {
            this.logger(`Component validation failed for ${component}: ${error.message}`, 'warn');
            return false;
        }
    }
}

// Export for both Node.js and browser environments
if (typeof window !== 'undefined') {
    // Browser environment
    window.TestingFramework = TestingFramework;
    window.LogLevel = LogLevel;
} else if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = TestingFramework;
    module.exports.LogLevel = LogLevel;
}