//=================================================================================
//
// TODO: Here's the updated internal logic:
//
// - On startup, report the initial screen
// - Report user actions (mouse, keyboard, navigation) as events
// - Report changes in screen content as events, triggered by user actions
//
// - Screen is stable when two consecutive screen reports 500ms apart report
//   the same screen.

// Configuration settings
const EXTENSION_CONFIG = {
    showPasswordValues: false  // Will be loaded from chrome.storage.local
};

// Tab Session ID using sessionStorage for proper tab isolation - enhanced for persistence
let CURRENT_TAB_SESSIONID = sessionStorage.getItem('tabSessionId');
if (!CURRENT_TAB_SESSIONID) {
    CURRENT_TAB_SESSIONID = 'tab_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    sessionStorage.setItem('tabSessionId', CURRENT_TAB_SESSIONID);
    console.log('Generated new tab ID:', CURRENT_TAB_SESSIONID);
} else {
    console.log('Using existing tab ID:', CURRENT_TAB_SESSIONID);
}

// Register the tab ID with the background script for tab close handling
function registerTabIdWithBackground() {
    chrome.runtime.sendMessage({
        type: 'registerTabId',
        tabId: CURRENT_TAB_SESSIONID
    }, (response) => {
        if (response && response.success) {
            console.log('Tab ID registered with background script');
        }
    });
}

// Send heartbeats to keep the session alive
function startHeartbeat() {
    const HEARTBEAT_INTERVAL = 60000; // 60 seconds
    
    setInterval(() => {
        // Only send heartbeats when tab is visible
        if (document.visibilityState === 'visible') {
            console.log('Sending heartbeat for tab:', CURRENT_TAB_SESSIONID);
            
            fetch(`http://localhost:3001/sessions/${CURRENT_TAB_SESSIONID}/heartbeat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-tab-id': CURRENT_TAB_SESSIONID
                }
            }).catch(err => {
                console.log('Heartbeat failed:', err);
            });
        }
    }, HEARTBEAT_INTERVAL);
}

// Register tab ID immediately
registerTabIdWithBackground();

// Start heartbeat when page is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startHeartbeat);
} else {
    startHeartbeat();
}

// Load settings from storage
async function loadExtensionSettings() {
    try {
        const result = await chrome.storage.local.get(['showPasswordValues']);
        EXTENSION_CONFIG.showPasswordValues = result.showPasswordValues || false;
    } catch (error) {
        console.error('Error loading extension settings:', error);
    }
}

// Listen for setting changes from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'settingChanged' && message.setting === 'showPasswordValues') {
        EXTENSION_CONFIG.showPasswordValues = message.value;
        console.log('Password visibility setting changed:', message.value);
    }
});

// Load settings on startup
loadExtensionSettings();
//
//=================================================================================
//
// --> Reports changes in screen content, and user interactions to the server
//     as events. Sends them to the server, immediately.
//
//     - Currently is read-only, no ability to send events to the browser.
//
//     - Doesn't use screen stability to judge when to report screen updates.
//       Looks like it's using time since the last DOM change only. Is that
//       good enough?
//
//     - Does not report user changes of URL as an event, though it's apparent
//       from the chnage in screen status. (Do we get URL change as an event?)
//
//     - Makes an effort to assign a label to an element based on the element's
//       position and content. (This is not always successful.)
//
//     - Would it be judicious to maintain a table of labels that have been
//       assigned to elements? (This would allow us to assign the same label
//       to the same element in subsequent events.)
//
//     - Can closely timed events intermingle with one another? (I think not,
//       but I'm not sure.)
//
//     - Can we get the URL of the page that generated the event?
//
const CONFIG = {
    changeDetectionDelay: 500, // ms NOT USED!
    serverUrl: 'http://localhost:3001'
};

const STABLE_SCREEN_DELAY = 300; // mS
const STABLE_SCREEN_MAX_WAIT = 2000; // mS
const DOUBLE_CLICK_THRESHOLD = 250; //mS

const INPUT_ATTRIBUTES = ['value', 'type', 'name', 'id', 'placeholder', /* 'disabled', */ 'readonly',
    'required', 'maxlength', 'minlength', 'pattern', 'autocomplete',
    'autofocus', 'checked', 'multiple', 'size', 'disabled', 'readonly',
    'minlength', 'required', 'maxlength', 'minlength', 'pattern',
    'autocomplete', 'autofocus', 'checked', 'multiple', 'size',
    'has_focus', 'validity state', 'aria-label', 'aria-required',
    'aria-invalid', 'aria-describedby', 'label text', /* 'form', */ 'position',
    'dimensions', 'visibility'];

// ## For Specific Input Types
// 19. **min/max** - For number and date inputs
// 20. **step** - For number inputs
// 21. **accept** - For file inputs (file types accepted)
// 22. **list** - ID of a datalist element providing suggestions

const SELECT_ATTRIBUTES = ['name', 'id', /* 'disabled', */ 'readonly', 'required', 'multiple', 'size',
    'has_focus', 'validity state', 'aria-label', 'aria-required',
    'aria-invalid', 'aria-describedby', 'label text', /* 'form', */
    'value', 'position', 'dimensions', 'visibility', 'options',
    'selectedIndex', 'selectedOptions',
    'value', 'text', 'selected'];

// Button attributes explanation:
// formaction: Specifies where to send form data (overrides form's action attribute)
// formenctype: Specifies how form data should be encoded before sending to server (for type="submit")
//              Values: application/x-www-form-urlencoded (default), multipart/form-data, text/plain
// formmethod: Specifies HTTP method for sending form data (GET/POST, overrides form's method)
// formnovalidate: Specifies that form shouldn't be validated when submitted (boolean attribute)
//              Useful for "Save Draft" or "Cancel" buttons to bypass validation
// formtarget: Specifies where to display response after form submission (overrides form's target)
const BUTTON_ATTRIBUTES = ['name', 'id', 'type', /*'disabled', */ /* 'form',*/ 'autofocus',
    'formaction', 'formenctype', 'formmethod', 'formnovalidate',
    'formtarget', 'value', 'has_focus', 'aria-label', 'aria-required',
    'aria-invalid', 'aria-describedby', 'label text', 'position',
    'dimensions', 'visibility'];

const TEXTAREA_ATTRIBUTES = ['name', 'id', 'placeholder', /* 'disabled', */ 'readonly', 'required',
    'maxlength', 'minlength', 'rows', 'cols', 'wrap', /* 'form', */
    'autofocus', 'has_focus', 'validity state', 'aria-label',
    'aria-required', 'aria-invalid', 'aria-describedby', 'label text',
    'value', 'position', 'dimensions', 'visibility'];

/**
 * Copies specified attributes for semantic control abstraction.
 * Filters out internal DOM properties while preserving user-visible state,
 * creating a clean interface between raw DOM elements and semantic representations.
 */
function copyAttributes(source, target, attr_list) {
    attr_list.forEach(attr => {
        if (source[attr] !== undefined) {
            target[attr] = source[attr];
        }
    })
    return target;
}

//=================================================================================
// SEMANTIC CONTROL DEFINITIONS - User-visible control abstractions
// 
// Status: DEFINITIONS COMPLETE - Ready for integration
// Next step: Modify returnElementProperties() to use detectSemanticControlType()
// and output semantic control JSON instead of raw DOM attributes
//=================================================================================

/**
 * SEMANTIC_CONTROL_DEFINITIONS - Generic User Framework Implementation
 * 
 * This defines the semantic abstraction layer that translates complex DOM structures
 * into human-meaningful control types that AI systems can understand and interact with.
 * 
 * Philosophy: Instead of making AI systems understand the complexity of HTML/CSS/DOM,
 * we present a simplified semantic view of "what a human would see" - buttons, inputs,
 * dropdowns, etc. This enables AI to browse the web using human-like mental models
 * rather than low-level DOM manipulation.
 * 
 * Each definition maps DOM patterns to semantic control types, allowing one abstraction
 * to handle many different HTML implementations of the same user interaction concept.
 */
const SEMANTIC_CONTROL_DEFINITIONS = [
    {
        id: 'INPUT_TEXT',
        visible_state: ['label', 'value', 'placeholder', 'is_focused', 'is_disabled'],
        actions: ['type', 'clear', 'focus', 'blur'],
        detection_rules: [
            {tagName: 'input', type: 'text'},
            {tagName: 'input', type: 'email'},
            {tagName: 'input', type: 'url'},
            {tagName: 'input', type: 'search'},
            {tagName: 'input', type: 'tel'}
        ]
    },
    {
        id: 'INPUT_PASSWORD',
        visible_state: ['label', 'is_masked', 'is_focused', 'is_disabled'],
        actions: ['type', 'clear', 'focus', 'blur', 'toggle_visibility'],
        detection_rules: [
            {tagName: 'input', type: 'password'}
        ]
    },
    {
        id: 'INPUT_DROPDOWN',
        visible_state: ['label', 'current_value', 'available_options', 'is_open', 'is_disabled'],
        actions: ['open', 'close', 'select_option', 'focus'],
        detection_rules: [
            {tagName: 'select'},
            {role: 'combobox'},
            {role: 'listbox'}
        ]
    },
    {
        id: 'INPUT_CHECKBOX',
        visible_state: ['label', 'is_checked', 'is_disabled'],
        actions: ['toggle', 'check', 'uncheck'],
        detection_rules: [
            {tagName: 'input', type: 'checkbox'}
        ]
    },
    {
        id: 'INPUT_RADIO',
        visible_state: ['label', 'is_selected', 'is_disabled', 'group_name'],
        actions: ['select'],
        detection_rules: [
            {tagName: 'input', type: 'radio'}
        ]
    },
    {
        id: 'INPUT_TEXTAREA',
        visible_state: ['label', 'value', 'placeholder', 'is_focused', 'is_disabled'],
        actions: ['type', 'clear', 'focus', 'blur'],
        detection_rules: [
            {tagName: 'textarea'}
        ]
    },
    {
        id: 'BUTTON_ACTION',
        visible_state: ['label', 'is_disabled', 'is_focused'],
        actions: ['click'],
        detection_rules: [
            {tagName: 'button', type: 'button'},
            {tagName: 'input', type: 'button'},
            {role: 'button'}
        ]
    },
    {
        id: 'BUTTON_SUBMIT',
        visible_state: ['label', 'is_disabled', 'is_focused'],
        actions: ['click', 'submit'],
        detection_rules: [
            {tagName: 'button', type: 'submit'},
            {tagName: 'input', type: 'submit'}
        ]
    },
    {
        id: 'LINK',
        visible_state: ['label', 'destination_hint'],
        actions: ['click', 'open_new_tab'],
        detection_rules: [
            {tagName: 'a', hasHref: true}
        ]
    }
];

/**
 * Detects the semantic control type(s) for a given DOM element
 * @param {Element} element - The DOM element to analyze
 * @returns {Array<number>} Array of indexes into SEMANTIC_CONTROL_DEFINITIONS that match
 */
function detectSemanticControlType(element) {
    const elementProps = {
        tagName: element.tagName.toLowerCase(),
        type: element.type?.toLowerCase(),
        role: element.getAttribute('role'),
        hasHref: !!element.href
    };

    // Return array of matching control definition indexes
    return SEMANTIC_CONTROL_DEFINITIONS
        .map((def, index) => ({def, index}))
        .filter(({def}) =>
            def.detection_rules.some(rule =>
                Object.entries(rule).every(([key, value]) =>
                    elementProps[key] === value
                )
            )
        )
        .map(({index}) => index);
}

/**
 * Gets the semantic control definition by index
 * @param {number} index - Index into SEMANTIC_CONTROL_DEFINITIONS
 * @returns {Object|null} Control definition or null if invalid index
 */
function getSemanticControlDefinition(index) {
    return SEMANTIC_CONTROL_DEFINITIONS[index] || null;
}

/**
 * Builds a semantic control element with user-visible attributes only
 * @param {Element} node - The DOM node
 * @param {Object} semanticDef - Semantic control definition
 * @param {Object} positionData - Position information from returnElementPosition
 * @param {string|null} existingLabel - Label from previous screen or other source
 * @returns {Object} Semantic element with prioritized field order
 */
/**
 * Add dropdown-specific state to semantic element
 * @param {Object} element - Element object to modify
 * @param {HTMLElement} node - The select element
 */
function addDropdownSemanticState(element, node) {
    const options = Array.from(node.options || []);
    const selectedOptions = Array.from(node.selectedOptions || []);

    // Handle both single and multi-select properly
    const isMultiSelect = node.multiple || node.type === 'select-multiple';
    
    if (selectedOptions.length === 0) {
        element.current_selection = '(none selected)';
        element.current_value = isMultiSelect ? [] : null;
    } else if (selectedOptions.length === 1) {
        element.current_selection = selectedOptions[0].text;
        element.current_value = isMultiSelect ? [selectedOptions[0].value] : selectedOptions[0].value;
    } else {
        // Multi-select: show arrays
        element.current_selection = selectedOptions.map(opt => opt.text);
        element.current_value = selectedOptions.map(opt => opt.value);
    }

    element.clickable_options = options
        .filter(opt => opt.value !== '') // Skip placeholder options
        .map(opt => `"${opt.text}" → ${opt.value}`);
    element.is_open = node.matches(':focus') && node.size > 1; // Approximate open state
    element.is_disabled = node.disabled || false;
}

/**
 * Add password-specific state to semantic element
 * @param {Object} element - Element object to modify
 * @param {HTMLElement} node - The password input element
 */
function addPasswordSemanticState(element, node) {
    element.is_focused = document.activeElement === node;
    element.is_disabled = node.disabled || false;
    
    // Handle password value based on showPasswordValues setting
    if (EXTENSION_CONFIG.showPasswordValues) {
        // Include actual password value when setting is enabled
        element.value = node.value || '';
        element.is_masked = false;
    } else {
        // Omit value entirely when masking is enabled (no value field at all)
        element.is_masked = true;
        // Note: deliberately NOT setting element.value for security
    }
}

/**
 * Add link-specific state to semantic element
 * @param {Object} element - Element object to modify
 * @param {HTMLElement} node - The link element
 */
function addLinkSemanticState(element, node) {
    element.destination_hint = node.href || null;
}

/**
 * Add generic interactive element state to semantic element
 * @param {Object} element - Element object to modify
 * @param {HTMLElement} node - The interactive element
 */
function addGenericSemanticState(element, node) {
    element.value = 'value' in node ? node.value : null;
    element.placeholder = node.placeholder || null;
    element.is_focused = document.activeElement === node;
    element.is_disabled = node.disabled || false;
    
    // Capture checkbox/radio specific properties
    if (node.type === 'checkbox' || node.type === 'radio') {
        element.checked = node.checked;
    }
    
    // Capture select-specific properties
    if (node.tagName === 'SELECT') {
        element.selectedOptions = Array.from(node.selectedOptions || []);
        element.multiple = node.multiple;
        element.selectedIndex = node.selectedIndex;
    }
}

/**
 * Build semantic element with proper priority ordering
 * @param {HTMLElement} node - The DOM element
 * @param {Object} semanticDef - Semantic definition object
 * @param {Object} positionData - Element position data
 * @param {string} existingLabel - Pre-existing label if any
 * @returns {Object} - Semantic element object
 */
function buildSemanticElement(node, semanticDef, positionData, existingLabel = null) {
    // Master Creator - ALL field assignments in priority order
    // JavaScript object property order is determined by assignment order!
    const element = {};

    // Priority 1: Label (most important for AI)
    element.label = existingLabel;

    // Priority 2: Control type (semantic classification)
    element.control_type = semanticDef.id;

    // Priority 3: Basic element identification
    element.tagName = node.tagName?.toLowerCase();
    element.type = node.type?.toLowerCase();

    // Priority 4: User-visible state (semantic-specific)
    switch (semanticDef.id) {
        case 'INPUT_DROPDOWN':
            addDropdownSemanticState(element, node);
            break;
        case 'INPUT_PASSWORD':
            addPasswordSemanticState(element, node);
            break;
        case 'LINK':
            addLinkSemanticState(element, node);
            break;
        default:
            addGenericSemanticState(element, node);
            break;
    }

    // Priority 5: Special attributes (only if relevant)
    if (node.href) {
        element.href = node.href;
    }

    // Priority 6: Position data (for targeting)
    element.top = positionData.top;
    element.left = positionData.left;
    element.bottom = positionData.bottom;
    element.right = positionData.right;

    // Priority 7: Node reference (always last, for internal use)
    element.node = node;

    return element;
}

let previousScreen = null;


// Configuration
function isTextElement(element) {
    node = typeof element.node === 'undefined' ? element : element.node;
    // --> If it's editable, is it really just text?
    if (node && node.getAttribute && node.getAttribute('contenteditable') === 'true') {
        return false;
    }
    return ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li'].includes(node.tagName.toLowerCase());
}

function isInteractiveElement(element) {
    node = typeof element.node === 'undefined' ? element : element.node;
    // Check tag name first
    // log(`isInteractiveElement: node: ${node}, typeof node: ${typeof node}, node.tagName: ${node.tagName}, typeof node.tagName is ${typeof node.tagName}`);
    if (typeof node.tagName === 'undefined') {
        return false;
    }
    if (['a', 'button', 'input', 'select', 'textarea', 'details', 'summary', 'dialog'].includes(node.tagName.toLowerCase())) {
        return true;
    }

    // Check for contenteditable attribute if element is provided
    if (node && node.getAttribute && node.getAttribute('contenteditable') === 'true') {
        return true;
    }

    // Check for ARIA roles that make elements interactive
    if (node && node.getAttribute) {
        const role = node.getAttribute('role');
        if (['button', 'combobox', 'listbox'].includes(role)) {
            return true;
        }
    }

    return false;
}

// Function to log messages to remote server log:
async function log(message) {
    try {
        const response = await fetch(`${CONFIG.serverUrl}/sessions/${CURRENT_TAB_SESSIONID}/events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Tab-ID': CURRENT_TAB_SESSIONID
            },
            body: JSON.stringify({type: 'log', data: message})
        });

        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }

    } catch (error) {
        // Log the error but don't throw - we'll try the fallback
        console.warn(`log:Failed to send log entry to server ${CONFIG.serverUrl} \n ${error.message}\n${error.stack}`);
    }
}

// Handle uncaught exceptions
window.addEventListener('error', (event) => {
    log(`window.addEventListener.error: === UNCAUGHT EXCEPTION ===\n\t${event.error.message}\n${event.error.stack}`);
});

// Event tracking
let lastEventTime = Date.now();
let changeDetectionTimeout = null;

//
// Extract the best label from a label dictionary or return string as-is
// Priority: Parent_Label, Left_Label, control, text, or first available key
//
function extractBestLabel(label) {
    if (typeof label === 'string') {
        return label;
    }
    
    if (typeof label === 'object' && label !== null) {
        // Priority order for label extraction
        const priorities = ['Parent_Label', 'Left_Label', 'control', 'text'];
        
        for (const key of priorities) {
            if (label[key] && typeof label[key] === 'string') {
                return label[key];
            }
        }
        
        // Fallback: return first string value found
        for (const [key, value] of Object.entries(label)) {
            if (typeof value === 'string' && value.trim() !== '') {
                return value;
            }
        }
        
        // Last resort: stringify the object
        return JSON.stringify(label);
    }
    
    return String(label);
}

//
// Find the label associated with an element
//
function addLabel(element, elements) {
    // todo: Search for label to the left of the input element
    // todo: Search for the label above the input element
    labels = element?.labels ? element.labels : {};

    // Handle all button types properly
    if (element.tagName.toLowerCase() === 'button') {
        element.label = element.node.textContent.trim();
    } else if (element.tagName.toLowerCase() === 'input' && element.node.type === 'button') {
        // Input buttons use value attribute, not textContent
        element.label = element.node.value || '';
    } else if (element.node.getAttribute && element.node.getAttribute('role') === 'button') {
        // ARIA buttons use textContent
        element.label = element.node.textContent.trim();
    }

    // if anchor, use text!
    if (element.tagName.toLowerCase() === 'a') {
        element.label = element.node.textContent.trim();
        if (element.label === '') {
            text = '';
            element.node.childNodes.forEach(node => {
                text += node.alt || node.textContent;
            })
            if (text !== '') {
                element.label = text.trim();
            }
        }
    }

    // Check for explicit label association
    if (!element.label && element.node.id) {
        const label = document.querySelector(`label[for="${element.node.id}"]`);
        if (label) {
            element.label = label.textContent.trim();
        }
    }

    // Check for implicit label association (label wrapping the element)
    if (!element.label && typeof element.node.closest === 'function') {
        log(`Considering Parent_Label...`);
        const parentLabel = element.node.closest('label');
        if (parentLabel) {
            labels.Parent_Label = parentLabel.textContent.trim();
        }
    }

    // Note: Search for a Label to the left of the element. If the label has been determined
    //       above, use that because it's more likely to be correct...
    if (!element.label) {
        prev = null;
        // search for element to the left and not below the element
        for (const el of elements) {
            el_midpoint = (el.top + el.bottom) / 2;
            if (el_midpoint > element.top && el_midpoint > element.bottom
                && el.right < element.left) {
                // found an item to the left of the element
            } else {
                // is this the element we're searching for a label for?
                if (el === element) {
                    // If we found the element, stop searching
                    if (prev && isTextElement(prev)) {
                        // if the element to the left is textual, assume it's a label
                        labels.Left_Label = prev.textContent.trim();
                    }
                }
                break;
            }
        }
    }

    if (!element.label && Object.keys(labels).length > 0) {
        element.label = extractBestLabel(labels);
    }
}

// Helper function to get element position for sorting
function returnElementPosition(element) {
    if (typeof element.getBoundingClientRect === 'function') {
        const rect = element.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            bottom: rect.bottom + window.scrollY,
            right: rect.right + window.scrollX,
        };
    }
    if (typeof element?.node?.getBoundingClientRect === 'function') {
        const rect = element.node.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            bottom: rect.bottom + window.scrollY,
            right: rect.right + window.scrollX,
        };
    }
    // Actually, this should never happen
    return {
        top: -1,
        left: -1,
        bottom: -1,
        right: -1,
    }
}

// Helper function to get element properties with semantic control detection
function returnElementProperties(element) {
    // Note: Element may be a DOM node, or a dictionary with a node entry.
    //       Also, the proper label might not have been found yet!
    const node = typeof element.node === 'undefined' ? element : element.node;
    const positionData = returnElementPosition(element);

    // Check if element exists on previous screen to preserve label
    let existingLabel = null;
    if (previousScreen) {
        previousScreen.visible_elements.forEach((screenElement) => {
            if (screenElement.node && screenElement.node.id === node.id) {
                existingLabel = screenElement.label;
            }
        });
    }

    // Try semantic control detection for interactive elements
    if (isInteractiveElement(node)) {
        const semanticIndexes = detectSemanticControlType(node);

        if (semanticIndexes.length > 1) {
            // Multiple matches - this is an error condition that should be visible
            const matchedTypes = semanticIndexes.map(i => SEMANTIC_CONTROL_DEFINITIONS[i].id);
            sendEvent('Warning', {
                returnElementProperties: `Multiple semantic control matches for ${node.tagName}[type="${node.type}"][id="${node.id}"]: ${matchedTypes.join(', ')} - using first match`
            });
        }

        if (semanticIndexes.length > 0) {
            // Use first matching semantic control type
            const semanticDef = getSemanticControlDefinition(semanticIndexes[0]);
            return buildSemanticElement(node, semanticDef, positionData, existingLabel);
        }
    }

    // Fallback for non-interactive elements (text content, etc.)
    const elem = {
        label: existingLabel,
        tagName: node.tagName?.toLowerCase(),
        textContent: null,
        top: positionData.top,
        left: positionData.left,
        bottom: positionData.bottom,
        right: positionData.right,
        has_focus: document.activeElement === node,
        node: node
    };

    // Add href only if the element actually has one
    if (node.href) {
        elem.href = node.href;
    }

    // Add text content for non-interactive elements
    if (!isInteractiveElement(node)) {
        elem.textContent = node?.textContent?.trim();
    }

    // Add href for links that weren't caught by semantic detection
    if (node?.href) {
        elem.href = node.href;
    }

    return elem;
}

/**
 * Get base event modifiers from event object
 * @param {Event} event - The DOM event
 * @returns {Object} - Modifier keys state
 */
function getEventModifiers(event) {
    return {
        ctrl: event.ctrlKey,
        shift: event.shiftKey,
        alt: event.altKey,
        meta: event.metaKey
    };
}

/**
 * Build structured target for dropdown (SELECT) elements
 * @param {HTMLElement} node - The SELECT element
 * @param {Event} event - The DOM event
 * @param {Object} target - Target information
 * @param {string} context - 'mouse' or 'keyboard'
 * @returns {Object} - Structured target object
 */
function buildDropdownTarget(node, event, target, context) {
    const selectedOptions = Array.from(node.selectedOptions);
    
    // Build unified dictionary: display_name -> actual_value
    const valueDict = {};
    selectedOptions.forEach(option => {
        valueDict[option.text] = option.value;
    });
    
    const result = {
        label: extractBestLabel(target.label) || 'Dropdown',
        value: valueDict,
        event_state: {
            modifiers: getEventModifiers(event)
        }
    };

    if (context === 'mouse') {
        const clickedOption = event.target.tagName === 'OPTION' ? event.target.text : null;
        result.event_state.clicked_option = clickedOption;
    }

    return result;
}

/**
 * Build structured target for radio button elements
 * @param {HTMLElement} node - The radio input element
 * @param {Event} event - The DOM event
 * @param {Object} target - Target information
 * @returns {Object} - Structured target object
 */
function buildRadioTarget(node, event, target) {
    const radioLabel = node.labels?.[0]?.textContent?.trim() || node.value || 'Option';
    
    // Build unified dictionary: display_name -> actual_value
    const valueDict = {};
    valueDict[radioLabel] = node.value;
    
    return {
        label: extractBestLabel(target.label) || node.name || radioLabel,
        value: valueDict,
        event_state: {
            modifiers: getEventModifiers(event)
        }
    };
}

/**
 * Build structured target for checkbox elements
 * @param {HTMLElement} node - The checkbox input element
 * @param {Event} event - The DOM event
 * @returns {Object} - Structured target object
 */
function buildCheckboxTarget(node, event) {
    const checkboxLabel = node.labels?.[0]?.textContent?.trim() || 'Checkbox';
    
    // Build unified dictionary: display_name -> actual_value
    const valueDict = {};
    valueDict[checkboxLabel] = node.checked;
    
    return {
        label: checkboxLabel,
        value: valueDict,
        event_state: {
            modifiers: getEventModifiers(event)
        }
    };
}

/**
 * Build structured target for text input and textarea elements
 * @param {HTMLElement} node - The input or textarea element
 * @param {Event} event - The DOM event
 * @param {Object} target - Target information
 * @returns {Object} - Structured target object
 */
function buildTextInputTarget(node, event, target) {
    const inputLabel = node.labels?.[0]?.textContent?.trim() || extractBestLabel(target.label) || 'Input';

    // Handle password masking - omit value entirely when masking enabled
    let fieldValue = node.value || '';
    const valueDict = {};
    
    if (node.type === 'password' && !EXTENSION_CONFIG.showPasswordValues) {
        // Don't include value at all for masked passwords
        // (valueDict remains empty)
    } else {
        // Build unified dictionary: display_name -> actual_value
        valueDict[fieldValue] = fieldValue; // For text inputs, display and value are the same
    }

    return {
        label: inputLabel,
        value: valueDict,
        event_state: {
            modifiers: getEventModifiers(event)
        }
    };
}

/**
 * Build structured target for option elements (fallback)
 * @param {HTMLElement} node - The option element
 * @param {Event} event - The DOM event
 * @returns {Object} - Structured target object
 */
function buildOptionTarget(node, event) {
    const selectElement = node.closest('select');
    const selectLabel = selectElement?.labels?.[0]?.textContent?.trim() || 'Dropdown';
    
    // Build unified dictionary: display_name -> actual_value
    const valueDict = {};
    valueDict[node.text] = node.value;
    
    return {
        label: selectLabel,
        value: valueDict,
        event_state: {
            modifiers: getEventModifiers(event)
        }
    };
}

/**
 * Unified function to build structured targets for any control type
 * @param {HTMLElement} node - The DOM element
 * @param {Event} event - The DOM event  
 * @param {Object} target - Target information
 * @param {string} context - 'mouse' or 'keyboard'
 * @returns {Object|null} - Structured target object or null
 */
function buildStructuredTarget(node, event, target, context) {
    // Dropdowns (SELECT elements)
    if (node.tagName === 'SELECT' && node.selectedOptions.length > 0) {
        return buildDropdownTarget(node, event, target, context);
    }

    // Radio buttons
    if (node.type === 'radio' && node.name) {
        return buildRadioTarget(node, event, target);
    }

    // Checkboxes
    if (node.type === 'checkbox') {
        return buildCheckboxTarget(node, event);
    }

    // Text inputs and textareas
    if (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA') {
        return buildTextInputTarget(node, event, target);
    }

    // Option elements (fallback)
    if (node.tagName === 'OPTION') {
        return buildOptionTarget(node, event);
    }

    return null; // No structured target for this element type
}

// Helper function to create fallback target structure when buildStructuredTarget fails
function createFallbackTarget(target, event) {
    if (target?.label) {
        return {
            label: {
                control: target.label,
                control_id: target.id || event?.target?.id || ""
            },
            value: {},
            event_state: {}
        };
    }
    
    // If target is null/undefined, create basic fallback from event
    if (!target && event?.target) {
        return {
            label: {
                control: event.target.textContent?.trim().substring(0, 50) || event.target.tagName || 'unknown',
                control_id: event.target.id || 'no-id'
            },
            value: {},
            event_state: {}
        };
    }
    
    return target || {};
}

// Helper function to get keyboard event properties
function returnKeyboardEventProperties(event) {
    target = returnElementProperties(event.target);

    // Build structured target using shared function
    let structuredTarget = null;

    if (event.target) {
        const node = event.target;

        // Check if this is a control key interaction we want to capture
        const isControlKeyInteraction =
            (node.tagName === 'SELECT' && (event.key === 'Enter' || event.key === ' ')) ||
            (node.type === 'radio' && (event.key.startsWith('Arrow') || event.key === ' ')) ||
            (node.type === 'checkbox' && event.key === ' ') ||
            (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA');

        if (isControlKeyInteraction) {
            structuredTarget = buildStructuredTarget(node, event, target, 'keyboard');

            // Log when we fall back to generic label due to poor labeling
            if (structuredTarget && !target.label && node.id) {
                sendEvent('log', {
                    message: `Using generic label for ${node.tagName.toLowerCase()} (keyboard) - poor UI labeling detected`,
                    element_id: node.id,
                    element_tag: node.tagName,
                    element_type: node.type,
                    key_pressed: event.key,
                    page_url: window.location.href
                });
            }
        }
    }

    return {
        tagName: event.tagName,
        target: structuredTarget || createFallbackTarget(target, event),
        key: event.key,
        code: event.code,
    };
}

/**
 * Resolve the actual target element for mouse events
 * @param {Event} event - The mouse event
 * @returns {Element} - The resolved target element
 */
function resolveEventTarget(event) {
    let targetElement = event.target;
    
    // Handle OPTION -> SELECT mapping
    if (event.target && event.target.tagName === 'OPTION') {
        targetElement = event.target.closest('select');
    }
    
    return targetElement;
}

/**
 * Find matching element in current screen data
 * @param {Element} targetElement - The target DOM element
 * @returns {Object|null} - Matching screen element or null
 */
function findMatchingScreenElement(targetElement) {
    const currentScreen = getCurrentScreen();
    return currentScreen.visible_elements.find(element => 
        element.node === targetElement
    ) || null;
}

/**
 * Build mouse event properties for matching screen elements
 * @param {Event} event - The mouse event
 * @param {Object} matchingElement - The matching screen element
 * @param {Element} targetElement - The target DOM element
 * @returns {Object} - Complete event properties object
 */
function buildMatchingEventProperties(event, matchingElement, targetElement) {
    log(`Mouse click: Found matching element with label "${matchingElement.label}" for ${targetElement.tagName}[id="${targetElement.id}"]`);
    
    return {
        event: event.type,
        target: {
            label: matchingElement.label,
            control_type: matchingElement.control_type,
            tagName: matchingElement.tagName,
            type: matchingElement.type || "",
            href: matchingElement.href,
            destination_hint: matchingElement.destination_hint,
            top: matchingElement.top,
            left: matchingElement.left,
            bottom: matchingElement.bottom,
            right: matchingElement.right,
            id: matchingElement.id || ""
        },
        y: event.clientY || 0,
        x: event.clientX || 0,
        button: event.button || 0,
        buttons: event.buttons || 0,
    };
}

/**
 * Build fallback mouse event properties for non-matching elements
 * @param {Event} event - The mouse event
 * @param {Element} targetElement - The target DOM element
 * @returns {Object} - Fallback event properties object
 */
function buildFallbackEventProperties(event, targetElement) {
    log(`Mouse click: No matching element found for ${targetElement.tagName}[id="${targetElement.id}"] - element not in visible list`);
    
    return {
        event: event.type,
        target: {
            label: targetElement.textContent?.trim() || targetElement.tagName,
            control_type: 'UNKNOWN',
            tagName: targetElement.tagName,
            type: targetElement.type || "",
            id: targetElement.id || ""
        },
        y: event.clientY || 0,
        x: event.clientX || 0,
        button: event.button || 0,
        buttons: event.buttons || 0,
    };
}

/**
 * Build minimal error fallback event properties
 * @param {Event} event - The mouse event
 * @param {Element} targetElement - The target DOM element (may be null)
 * @returns {Object} - Minimal event properties object
 */
function buildErrorEventProperties(event, targetElement) {
    return {
        event: 'click',
        target: {
            label: 'unknown',
            control_type: 'UNKNOWN',
            tagName: targetElement?.tagName || 'unknown',
            type: "",
            id: targetElement?.id || ""
        },
        y: event.clientY || 0,
        x: event.clientX || 0,
        button: event.button || 0,
        buttons: event.buttons || 0,
    };
}

/**
 * Get mouse event properties with target resolution and screen matching
 * @param {Event} event - The mouse event to process
 * @returns {Object} - Structured event properties object
 */
function getMouseEventProperties(event) {
    try {
        const targetElement = resolveEventTarget(event);
        const matchingElement = findMatchingScreenElement(targetElement);
        
        if (matchingElement) {
            return buildMatchingEventProperties(event, matchingElement, targetElement);
        } else {
            return buildFallbackEventProperties(event, targetElement);
        }
        
    } catch (error) {
        console.error('Error in getMouseEventProperties:', error);
        return buildErrorEventProperties(event, event.target);
    }
}

function collectAllVisibleElements() {
    const elements = [];
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT,
        {
            acceptNode: function (node) {
                // Skip hidden elements and their children
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const style = window.getComputedStyle(node);
                    if (style.display === 'none' || style.visibility === 'hidden') {
                        return NodeFilter.FILTER_REJECT;
                    }
                }
                if (typeof node.tagName === 'undefined') {
                    return NodeFilter.FILTER_REJECT;
                }
                // Skip empty/whitespace text nodes
                if (node.nodeType === Node.TEXT_NODE && (!node.nodeValue || /^[\s\r\n\t]*$/.test(node.nodeValue))) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );

    // Collect all visible nodes
    const allNodes = [];
    while (walker.nextNode()) {
        node = walker.currentNode;
        if (walker.currentNode.nodeType === Node.TEXT_NODE) {
            // isText = true;
            node = walker.currentNode.parentElement;
            if (isTextElement(node)) {
                // If the text node is part of a text node or interactive node, add it
                allNodes.push(walker.currentNode);
            }
            // if what we've got is bare text, it should have been captured with its parent node.
        } else {
            if (isInteractiveElement(node)) {
                allNodes.push(walker.currentNode);
            }
        }
    }

    // Process nodes to extract minimal required information
    return allNodes.map((node) => {
        const isText = node.nodeType === Node.TEXT_NODE;
        const element = isText ? node.parentElement : node;

        result = {
            ...(isText ? {} : {label: ''}),
            tagName: element.tagName?.toLowerCase(),
            ...(isInteractiveElement(element) && element.tagName?.toLowerCase() === 'a' ? {href: ''} : {}),
            ...(isInteractiveElement(element) && element.tagName?.toLowerCase() !== 'a' ? {type: ''} : {}),
            ...(isText ? {textContent: ''} : {}),
            ...returnElementPosition(element),
        };

        if (isText && isTextElement(result)) {
            // todo: improve this, I think to remove empty lines...
            result.textContent = node.textContent.trim();
        }

        // Only add interactive properties for interactive elements
        if (!isText && isInteractiveElement(node)) {
            result = returnElementProperties(element);
        }

        result.node = node;

        return result;
    }).sort((a, b) => a.top - b.top || a.left - b.left);
}

// Function to get screen status
function getCurrentScreen() {
    screen = {
        type: 'screen_status',
        url: window.location.href,
        focus_label: null,
        focus_id: document.activeElement?.id || null,
        visible_elements: collectAllVisibleElements(),      //  returnScreenCombinedElements(),
        showPasswordValues: EXTENSION_CONFIG.showPasswordValues, // Include setting state for change detection
    };
    // visible elements are returned already sorted
    screen.visible_elements.map((element) => {
        if (isInteractiveElement(element)) {
            // If the element is interactive, add its label if it has one
            addLabel(element, screen.visible_elements);
            if (element.has_focus && element.label) {
                screen.focus_label = element.label;
            }
        }
    });
    return screen;
}

// Event queue system for race-safe sending and centralized change detection
let eventQueue = [];
let sendingInProgress = false;
let changeDetectionTimer = null;

// Keyboard accumulation system
let inProcessKeyboard = null;

function flushPendingKeyboard() {
    if (inProcessKeyboard) {
        // Capture final text value at flush time for accuracy
        const targetElement = document.getElementById(inProcessKeyboard.target.label.control_id) ||
            document.querySelector(`[id="${inProcessKeyboard.target.label.control_id}"]`);
        if (targetElement) {
            let finalValue = targetElement.value || '';

            // Handle password masking - omit value entirely when masking enabled
            if (targetElement.type === 'password' && !EXTENSION_CONFIG.showPasswordValues) {
                // Don't include value field at all for masked passwords
                // (value property will be undefined/missing)
            } else {
                // Update unified dictionary format: display_name -> actual_value
                inProcessKeyboard.target.value = {};
                inProcessKeyboard.target.value[finalValue] = finalValue; // For text inputs, display = value
            }
        }

        sendEvent('keyboard', inProcessKeyboard);
        inProcessKeyboard = null;
    }
}

// Function to send event to server
async function sendEvent(kind, data) {
    // Queue the event with source attribution
    eventQueue.push({
        type: kind,
        ...data,
        source: window.actorExecuting ? 'actor' : 'user',
        timestamp: new Date().toISOString()
    });

    // Schedule screen change detection for all events EXCEPT screen_status
    if (kind !== 'screen_status') {
        scheduleChangeDetection();
    }

    // Process the queue
    processSendQueue();
}

// Schedule delayed screen change detection (cancels previous if pending)
function scheduleChangeDetection() {
    if (changeDetectionTimer) {
        clearTimeout(changeDetectionTimer);
    }
    changeDetectionTimer = setTimeout(() => {
        // Flush any pending keyboard input before capturing screen state
        flushPendingKeyboard();

        sendEvent('screen_status', getCurrentScreen());
        changeDetectionTimer = null;
    }, STABLE_SCREEN_DELAY);
}

// Process the event queue serially to prevent race conditions
function processSendQueue() {
    if (sendingInProgress || eventQueue.length === 0) {
        return; // Already sending or nothing to send
    }

    sendingInProgress = true;

    while (eventQueue.length > 0) {
        const event = eventQueue.shift(); // Atomic pop from front
        actuallySendEvent(event);
    }

    sendingInProgress = false;
}

// Helper function to clean event data for sending (remove internal fields)
function cleanEventForSending(event_) {
    // Deep clone the event and remove node fields recursively
    const cleanEvent = JSON.parse(JSON.stringify(event_, (key, value) => {
        // Filter out node fields and other internal properties
        if (key === 'node') {
            return undefined;
        }
        return value;
    }));

    return cleanEvent;
}

// The actual HTTP sending logic (extracted from original sendEvent)
async function actuallySendEvent(event_) {
    // Clean the event data before sending
    const cleanEvent = cleanEventForSending(event_);

    // Try to send to server first
    try {
        console.log(`actuallySendEvent session:${CURRENT_TAB_SESSIONID} event:${event_.type} data:${JSON.stringify(cleanEvent)}`);
        const response = await fetch(`${CONFIG.serverUrl}/sessions/${CURRENT_TAB_SESSIONID}/events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Tab-ID': CURRENT_TAB_SESSIONID
            },
            body: JSON.stringify(cleanEvent)
        });

        if (!response.ok) {
            throw new Error(`sendEvent: Server responded with status: ${response.status}`);
        }
    } catch (error) {
        // Log the error but don't throw - we'll try the fallback
        // console.warn('sendEvent: Failed to send event to server, trying fallback:', error);
        log(`sendEvent: Failed to send event ${event_.type} to server, trying fallback: ${error.message} \n ${error.stack}`);
        // Fallback: Send to background script
    }
}

// Function to report screen status
function screenChanged(currentScreen, lastScreen) {
    // Compare current screen with the provided last screen state
    changeDetected = !lastScreen || JSON.stringify(lastScreen?.visible_elements) !== JSON.stringify(currentScreen?.visible_elements);
    return changeDetected;
}

let stabilityTimer = null;
let stabilityStartTime = null;
let lastStabilityScreen = null;

function sendScreenContent() {
    // Cancel any existing stability monitoring
    if (stabilityTimer) {
        clearTimeout(stabilityTimer);
    }

    // Initialize stability tracking
    stabilityStartTime = Date.now();
    lastStabilityScreen = getCurrentScreen();

    // Start stability monitoring loop
    checkStabilityLoop();
}

function checkStabilityLoop() {
    const currentScreen = getCurrentScreen();
    const hasChanged = screenChanged(currentScreen, lastStabilityScreen);
    const timeElapsed = Date.now() - stabilityStartTime;

    if (!hasChanged || timeElapsed >= STABLE_SCREEN_MAX_WAIT) {
        // Screen is stable or we timed out - send it!
        previousScreen = currentScreen;
        sendEvent('screen_status', currentScreen);
        stabilityTimer = null;
        return;
    }

    // Still changing - update reference and check again
    lastStabilityScreen = currentScreen;
    stabilityTimer = setTimeout(checkStabilityLoop, STABLE_SCREEN_DELAY);
}

/**
 * Checks for changes in the current screen status and sends updated content if changes are detected.
 *
 * @global {Function} getCurrentScreen - Function to retrieve the current screen's status.
 * @global {Function} screenChanged - Function to determine if the screen has changed.
 * @global {Function} sendScreenContent - Function to send the current screen content if changes are detected.
 */
// Old changedScreenTimer and sendChangedScreenContent() replaced by queue system

// Function to register session with tab identity
async function registerSession() {
    try {
        const tabIdentity = {
            tabId: CURRENT_TAB_SESSIONID, // Use persistent tab ID instead of random ID
            url: window.location.href,
            title: document.title,
            windowId: null, // Not available in content script
            index: null     // Not available in content script
        };

        const response = await fetch(`${CONFIG.serverUrl}/sessions/init`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-Tab-ID': CURRENT_TAB_SESSIONID
            },
            body: JSON.stringify(tabIdentity)
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Session registered successfully:', result.sessionId);
        } else {
            console.error('Failed to register session:', response.status);
        }
    } catch (error) {
        console.error('Error registering session:', error);
    }
}

window.addEventListener('load', (event) => {
    // Flush any pending keyboard input from previous page
    flushPendingKeyboard();

    // Register this tab as a session
    registerSession();

    sendEvent('event', {
        event: 'load',
        url: window.location.href,
    });
});

// Double-click detection removed for simplicity

// Debug checkpoint before click listener
log('About to attach click listener');
sendEvent('log', { message: 'Click listener attachment point reached' });

// Add a simple test to ensure the listener is working
try {
    document.addEventListener('click', (event) => {
    // Send debug event immediately when ANY click detected
    sendEvent('log', { 
        message: `CLICK DETECTED on ${event.target.tagName}`,
        target_tag: event.target.tagName,
        target_id: event.target.id,
        x: event.clientX,
        y: event.clientY
    });
    
    log(`CLICK DETECTED: ${event.target.tagName} at ${event.clientX},${event.clientY}`);
    
    // Debug: check if this is a synthetic event
    if (event.clientX === 100 && event.clientY === 100) {
        log('Skipping synthetic test click');
        return; // Skip synthetic test clicks
    }
    
    // Process click immediately - no double-click delay
    // Flush any pending keyboard input before processing click
    flushPendingKeyboard();

    // Use queueMicrotask to read control state AFTER DOM updates complete
    queueMicrotask(() => {
        try {
            const mouseProps = getMouseEventProperties(event);
            
            sendEvent('mouse', {
                event: 'click',
                ...mouseProps,
            });
            log(`Mouse click processed: ${event.target.tagName}`);
        } catch (error) {
            log(`Mouse click error: ${error.message}\n${error.stack}`);
            
            // Send basic event without complex properties as fallback
            sendEvent('mouse', {
                event: 'click',
                target: {
                    label: {
                        control: event.target.textContent?.trim().substring(0, 50) || event.target.tagName || 'unknown',
                        control_id: event.target.id || 'no-id'
                    }
                },
                x: event.clientX,
                y: event.clientY,
                button: event.button,
                error: error.message
            });
        }
    });
    
    }); // Close the addEventListener callback
    
    log('Click listener attached successfully');
    sendEvent('log', { message: 'Click listener attached successfully' });
    
} catch (error) {
    log(`Error attaching click listener: ${error.message}`);
    sendEvent('log', { message: `Error attaching click listener: ${error.message}` });
}

// Double-click handler removed - treating all clicks as single clicks

// Unified keyboard handler with accumulation
document.addEventListener('keydown', (event) => {
    const currentTarget = event.target;
    const isTextInput = currentTarget.tagName === 'INPUT' &&
        (currentTarget.type === 'text' || currentTarget.type === 'email' ||
            currentTarget.type === 'search' || currentTarget.type === 'url' ||
            currentTarget.type === 'tel' || currentTarget.type === 'password') ||
        currentTarget.tagName === 'TEXTAREA';

    // Control keys - but EXCLUDE space for text inputs (space is part of typing)
    const isControlKey = event.key === 'Enter' ||
        (!isTextInput && event.key === ' ') ||
        (event.key && event.key.startsWith('Arrow')) ||
        event.key === 'Tab';

    // Exclude modifier keys from accumulation (they don't produce text)
    const isModifierKey = event.key === 'Shift' || event.key === 'Control' ||
        event.key === 'Alt' || event.key === 'Meta';

    // Control keys get sent immediately (navigation, form controls)
    if (isControlKey && isInteractiveElement(currentTarget)) {
        // Flush any pending text input first
        flushPendingKeyboard();

        // Send control key immediately using queueMicrotask for DOM updates
        queueMicrotask(() => {
            sendEvent('keyboard', {
                event: 'control_key',
                ...returnKeyboardEventProperties(event),
            });
        });
    }
    // Text input keys get accumulated (but skip modifier keys)
    else if (isTextInput && !isModifierKey) {
        const currentTargetInfo = returnElementProperties(currentTarget);

        // If target changed or first keystroke, start new accumulated event
        if (!inProcessKeyboard || inProcessKeyboard.target.label.control_id !== (currentTargetInfo.id || currentTarget.id)) {
            flushPendingKeyboard(); // Send any previous accumulated event

            // Handle password masking for initial value
            let initialValue = currentTarget.value || '';
            let includeValue = true;
            if (currentTarget.type === 'password' && !EXTENSION_CONFIG.showPasswordValues) {
                // For password fields with masking enabled, don't include value at all
                includeValue = false;
            }

            inProcessKeyboard = {
                event: 'text_input',
                target: {
                    label: {
                        control: currentTargetInfo.label || 'Text Input',
                        control_id: currentTargetInfo.id || currentTarget.id || ''
                    },
                    value: {}, // Will be set to unified dictionary format at flush time
                    event_state: {
                        keystrokes: [{
                            key: event.key,
                            key_code: event.code,
                            timestamp: new Date().toISOString(),
                            modifiers: {
                                ctrl: event.ctrlKey,
                                shift: event.shiftKey,
                                alt: event.altKey,
                                meta: event.metaKey
                            }
                        }]
                    }
                }
            };
        } else {
            // Same target, accumulate keystroke
            inProcessKeyboard.target.event_state.keystrokes.push({
                key: event.key,
                key_code: event.code,
                timestamp: new Date().toISOString(),
                modifiers: {
                    ctrl: event.ctrlKey,
                    shift: event.shiftKey,
                    alt: event.altKey,
                    meta: event.metaKey
                }
            });
        }

    }
});

// Blur event handler for keyboard accumulation management
document.addEventListener('blur', (event) => {
    // If we have active keyboard accumulation, flush it
    // (blur can only come from the field losing focus)
    if (inProcessKeyboard) {
        flushPendingKeyboard();
    }
}, true);

document.addEventListener('submit', (event) => {
    // Flush any pending keyboard input before form submission
    flushPendingKeyboard();

    // FIXME: Submit also has an associated URL...
    //        Not much information here...
    sendEvent('button', {
        event: 'submit',
        isSubmit: true,
        ...event,
    });
});

// Flush keyboard input before page unload
window.addEventListener('beforeunload', (event) => {
    flushPendingKeyboard();
});

// Also flush on page hide (for back/forward navigation)
window.addEventListener('pagehide', (event) => {
    flushPendingKeyboard();
});

// ========================================================================
// ACTOR CHANNEL - Commands flowing FROM server TO browser
// ========================================================================
function checkDefined(value) {
    t = typeof value;
    console.log(`typeof ${value.name} is ${t}`);
}

/**
 * Actor Channel State Management
 * Tracks whether it's safe to execute Actor commands without interfering with Observer
 */
let isExecutingActorCommand = false;

/**
 * Check if it's safe to execute Actor commands
 * Prevents interference with ongoing Observer activities
 */
function isSafeToExecuteActor() {
    // Don't interrupt ongoing keyboard accumulation
    if (inProcessKeyboard) {
        return false;
    }

    // Don't overlap Actor commands
    if (isExecutingActorCommand) {
        return false;
    }

    // Add other safety checks as needed
    // if (screenCaptureInProgress) return false;

    return true;
}

/**
 * Poll server for Actor commands and execute them when safe
 * Runs continuously in background, non-blocking
 */
async function pollForActorCommands() {
    log('Actor Channel: Starting command polling loop');
    sendEvent('log', { message: `Actor Channel: Starting polling for session ${CURRENT_TAB_SESSIONID}` });

    while (true) {
        try {
            // Poll server for pending commands
            const pollUrl = `${CONFIG.serverUrl}/sessions/${CURRENT_TAB_SESSIONID}/actor/commands`;
            const response = await fetch(pollUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Tab-ID': CURRENT_TAB_SESSIONID
                }
            });

            if (response.ok) {
                const commands = await response.json();

                if (commands.length > 0) {
                    log(`Actor Channel: Received ${commands.length} commands from server`);
                    sendEvent('log', { message: `Actor Channel: Received ${commands.length} commands from session ${CURRENT_TAB_SESSIONID}` });
                    console.log(`Actor Channel: Received ${commands.length} commands from server`);

                    // Process each command when safe
                    for (const command of commands) {
                        console.log(`🎯 POLLING DEBUG: Processing command: ${command.type} with data:`, command);
                        sendEvent('log', { message: `Actor Channel: Processing command ${command.id}: ${command.type}` });
                        await processActorCommandWhenSafe(command);
                    }
                }
            } else {
                // Log HTTP error responses for debugging
                sendEvent('log', { message: `Actor Channel: Poll failed with status ${response.status}: ${response.statusText}`, url: pollUrl });
            }
        } catch (error) {
            // Log fetch errors for debugging
            sendEvent('log', { message: `Actor Channel: Poll error: ${error.message}`, url: pollUrl });
            // Server not available or network error - continue polling
            // Don't log every polling error to avoid spam
            if (error.message && !error.message.includes('fetch')) {
                log(`Actor Channel: Polling error: ${error.message}`);
            }
        }

        // Non-blocking delay before next poll
        await new Promise(resolve => setTimeout(resolve, 100)); // Poll every 100ms
    }
}

/**
 * Process Actor command when it's safe to do so
 * Waits for safe execution window, then executes and echoes to Observer
 */
async function processActorCommandWhenSafe(command) {
    // Wait for safe execution window (with timeout)
    const maxWaitTime = 5000; // 5 second timeout
    const startTime = Date.now();

    console.log(`Actor Channel: Waiting for safe execution of command ${command.id}`);
    while (!isSafeToExecuteActor() && (Date.now() - startTime) < maxWaitTime) {
        await new Promise(resolve => setTimeout(resolve, 50)); // Check every 50ms
    }

    if (!isSafeToExecuteActor()) {
        log(`Actor Channel: Timeout waiting for safe execution of command ${command.id}`);
        return;
    }

    isExecutingActorCommand = true;

    try {
        try { log(`Actor Channel: Executing command ${command.id}: ${command.type}`); } catch(e) {}
        console.log(`Actor Channel: Executing command ${command.id}: ${command.type}`);
        await executeActorCommand(command);

        // Natural Observer events will detect DOM changes with proper source attribution

    } catch (error) {
        try { log(`Actor Channel: Error executing command ${command.id}: ${error.message}`); } catch(e) {}
    } finally {
        isExecutingActorCommand = false;
    }
}

/**
 * Find DOM element matching command target specification
 * Uses Observer's current screen data for reliable label-based matching with ID validation
 */
function findTargetElement(targetSpec) {
    if (!targetSpec || !targetSpec.label) {
        throw new Error('Actor: Target specification missing or invalid');
    }

    // Handle both old format {control, control_id} and new format (direct string)
    let control, control_id;
    if (typeof targetSpec.label === 'object' && targetSpec.label.control) {
        // Old format: {control: "text", control_id: "id"}
        control = targetSpec.label.control;
        control_id = targetSpec.label.control_id;
    } else {
        // New format: direct label string with id separate
        control = targetSpec.label;
        control_id = targetSpec.id;
    }
    
    // Primary strategy: Search current screen's visible_elements by label
    // This ensures we find exactly what the Observer "sees" and has labeled
    const currentScreen = getCurrentScreen();
    
    // TODO: Add URL validation - we'd expect currentScreen.url to match the URL 
    // when the command was issued. This could catch stale commands or navigation issues.
    
    // Use exact matching only - same strategy as TestingFramework
    const screenElement = currentScreen.visible_elements.find(element => {
        return element.label && element.label.toLowerCase() === control.toLowerCase();
    });

    if (!screenElement) {
        // Log available labels to help with debugging
        const availableLabels = currentScreen.visible_elements
            .map(el => el.label || 'unlabeled')
            .slice(0, 10);
        log(`Actor: No element found with exact label "${control}". Available labels: ${availableLabels.join(', ')}`);
        throw new Error(`Actor: No element found with label "${control}" in current screen`);
    }

    // Check for multiple matches and warn (but still use first match for consistency)
    const allMatches = currentScreen.visible_elements.filter(element => {
        return element.label && element.label.toLowerCase() === control.toLowerCase();
    });
    
    if (allMatches.length > 1) {
        log(`Actor: WARNING - Multiple elements (${allMatches.length}) found with label "${control}". Using first match. Consider improving label uniqueness.`);
    }

    let foundElement = screenElement.node;
    let matchMethod = 'exact_label_match';

    // Cross-validation: Double-check ID matches if provided (good practice until we trust pure labels)
    if (control_id && foundElement && foundElement.id !== control_id) {
        log(`Actor: WARNING - Label-based match found but ID mismatch. Expected: "${control_id}", Found: "${foundElement.id}"`);
        log(`Actor: This might indicate screen changes or labeling inconsistencies`);
        // Continue but flag the mismatch - this helps build confidence in the system
    }

    // Log successful match for debugging
    if (foundElement) {
        log(`Actor: Found target element via ${matchMethod} - ${foundElement.tagName}[id="${foundElement.id}"] with label "${screenElement.label}"`);
    } else {
        log(`Actor: WARNING - screenElement.node is null for label "${screenElement.label}". This indicates an architectural issue.`);
    }
    
    return {
        element: foundElement,
        screenElement: screenElement,  // Include the full screen element data
        matchMethod: matchMethod,
        validated: !control_id || (foundElement && foundElement.id === control_id)
    };
}

/**
 * Set value on different control types before triggering events
 * Handles the complexity of different HTML control value setting
 */
function setElementValue(element, newValue, controlType) {
    const tagName = element.tagName.toLowerCase();
    const inputType = element.type?.toLowerCase();

    try {
        switch (tagName) {
            case 'input':
                if (inputType === 'checkbox' || inputType === 'radio') {
                    // For checkboxes/radio: newValue should be boolean or 'checked'/'unchecked'
                    const shouldCheck = newValue === true || newValue === 'checked' || newValue === 'true';
                    element.checked = shouldCheck;
                    try { log(`Actor: Set ${inputType} to ${shouldCheck ? 'checked' : 'unchecked'}`); } catch(e) {}
                } else {
                    // Text inputs, password, email, etc.
                    if (newValue === undefined || newValue === null) {
                        element.value = '';  // Explicitly clear if no value provided
                    } else {
                        element.value = newValue;  // Use exactly what was provided
                    }
                    try { log(`Actor: Set input value to "${element.value}"`); } catch(e) {}
                }
                break;

            case 'select':
                // Dropdown: find option by text or value
                const options = Array.from(element.options);
                let targetOption = null;

                // Try to match by value first, then by text
                targetOption = options.find(opt => opt.value === newValue) ||
                              options.find(opt => opt.text === newValue);

                if (targetOption) {
                    element.selectedIndex = targetOption.index;
                    try { log(`Actor: Set select to option "${targetOption.text}" (value: "${targetOption.value}")`); } catch(e) {}
                } else {
                    throw new Error(`Actor: Could not find option "${newValue}" in dropdown`);
                }
                break;

            case 'textarea':
                if (newValue === undefined || newValue === null) {
                    element.value = '';  // Explicitly clear if no value provided
                } else {
                    element.value = newValue;  // Use exactly what was provided
                }
                try { log(`Actor: Set textarea value to "${element.value}"`); } catch(e) {}
                break;

            default:
                // For buttons, links, etc. - no value to set
                try { log(`Actor: No value to set for ${tagName} element`); } catch(e) {}
        }

        return true;
    } catch (error) {
        try { log(`Actor: Error setting value on ${tagName}: ${error.message}`); } catch(e) {}
        throw error;
    }
}

/**
 * Execute the actual Actor command
 * Handles different command types with proper source tagging and native browser methods
 */
async function executeActorCommand(command) {
    console.log(`🚀 EXECUTE ENTRY: executeActorCommand called with command type: "${command.type}"`);
    log(`Actor Channel: Executing ${command.type} command`);

    // Set global flag to mark subsequent Observer events as Actor-generated
    window.actorExecuting = true;
    try { log(`Actor Channel: Setting actorExecuting flag for command: ${command.type}`); } catch(e) {}

    try {
        console.log(`🔍 EXECUTE DEBUG: About to switch on command type: "${command.type}"`);
        switch (command.type) {
            case 'screen_status':
                // Quietly ignore screen_status commands - browser generates its own reports
                log(`Actor Channel: Ignoring screen_status command (browser will generate own reports)`);
                break;

            case 'test_actor_channel':
                // Test command - just log and echo back
                log(`Actor Channel: Test command received: ${command.data.message}`);
                break;

            case 'mouse':
                try {
                    const target = findTargetElement(command.target);
                    log(`Actor Channel: Clicking element ${target.element.tagName}[id="${target.element.id}"]`);
                    
                    // For state-changing controls, set values from dictionary
                    if (command.target?.value && typeof command.target.value === 'object') {
                        const element = target.element;
                        const tagName = element.tagName.toLowerCase();
                        
                        if (tagName === 'select') {
                            // Handle dropdown selections - set selected options
                            const targetValues = Object.values(command.target.value);
                            Array.from(element.options).forEach(option => {
                                option.selected = targetValues.includes(option.value);
                            });
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                        } else if (element.type === 'checkbox' || element.type === 'radio') {
                            // Handle checkbox/radio - set checked state
                            const values = Object.values(command.target.value);
                            element.checked = values.includes(true);
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                    
                    // Use native browser click method for authentic events
                    target.element.click();
                    
                } catch (error) {
                    log(`Actor Channel: Mouse click failed: ${error.message}`);
                    // TODO: Add error attribute to natural Observer events
                }
                break;

            case 'keyboard':
                try {
                    console.log(`🔍 KEYBOARD DEBUG: Processing keyboard command with data:`, command.data);
                    console.log(`🔍 KEYBOARD DEBUG: Target specification:`, command.target);
                    const target = findTargetElement(command.target);
                    console.log(`🔍 KEYBOARD DEBUG: Found target element:`, target.element.tagName, target.element.type, target.element.id);
                    
                    // Extract value from sensible dictionary format only
                    let newValue = '';
                    if (command.target?.value && typeof command.target.value === 'object') {
                        // Use sensible "text" field - the only acceptable format
                        if (command.target.value.hasOwnProperty('text')) {
                            newValue = command.target.value.text;  // Use exactly what was provided (including empty string)
                        } else {
                            throw new Error(`Invalid keyboard command format: value must contain "text" field, got: ${JSON.stringify(command.target.value)}`);
                        }
                    } else {
                        throw new Error(`Invalid keyboard command: target.value must be an object with "text" field`);
                    }
                    
                    console.log(`🔍 KEYBOARD DEBUG: Extracted value: "${newValue}"`);
                    
                    // Set the value using native methods (actorExecuting flag already set by executeActorCommand)
                    target.element.focus();  // Focus first for proper event sequence
                    console.log(`🔍 KEYBOARD DEBUG: Before setting value, current value: "${target.element.value}"`);
                    
                    // Handle different element types specially
                    if (target.element.tagName === 'SELECT' && target.element.multiple) {
                        // Multi-select: parse comma-separated values and set option.selected
                        const selectedValues = newValue ? newValue.split(',').map(v => v.trim()) : [];
                        Array.from(target.element.options).forEach(option => {
                            option.selected = selectedValues.includes(option.value);
                        });
                        console.log(`🔍 KEYBOARD DEBUG: Multi-select set to: [${selectedValues.join(', ')}]`);
                    } else if (target.element.type === 'checkbox' || target.element.type === 'radio') {
                        // Checkboxes and radio buttons: set checked property
                        const shouldCheck = newValue === 'true' || newValue === true;
                        target.element.checked = shouldCheck;
                        console.log(`🔍 KEYBOARD DEBUG: ${target.element.type} set to checked: ${shouldCheck}`);
                    } else {
                        // Regular elements: set value directly
                        target.element.value = newValue;
                        console.log(`🔍 KEYBOARD DEBUG: After setting value, current value: "${target.element.value}"`);
                    }
                    
                    // Trigger native events for form validation and handlers
                    target.element.dispatchEvent(new Event('input', { bubbles: true }));
                    target.element.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    log(`Actor Channel: Set value "${newValue}" in ${target.element.tagName}[id="${target.element.id}"]`);
                    
                    // Natural Observer events will detect the DOM changes and generate proper events
                    // with source attribution to distinguish from user actions
                    
                } catch (error) {
                    log(`Actor Channel: Keyboard input failed: ${error.message}`);
                    // TODO: Add error attribute to natural Observer events
                }
                break;

            case 'set_value':
                try {
                    const target = findTargetElement(command.target);
                    const newValue = command.data?.value;
                    
                    // Set the value and trigger change event
                    setElementValue(target.element, newValue);
                    target.element.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    log(`Actor Channel: Set value "${newValue}" on ${target.element.tagName}[id="${target.element.id}"]`);
                    
                } catch (error) {
                    log(`Actor Channel: Set value failed: ${error.message}`);
                    // TODO: Add error attribute to natural Observer events
                }
                break;

            case 'load':
                try {
                    const targetUrl = command.target?.url;
                    if (!targetUrl) {
                        throw new Error('Load command requires target.url');
                    }
                    
                    log(`Actor Channel: Navigating to URL: ${targetUrl}`);
                    
                    // Use native browser navigation for authentic page load
                    window.location.href = targetUrl;
                    
                    // Note: No explicit success logging here as page will reload
                    // Success will be evident from subsequent screen_status events
                    
                } catch (error) {
                    log(`Actor Channel: Load navigation failed: ${error.message}`);
                    // TODO: Add error attribute to natural Observer events
                }
                break;

            default:
                // Log unrecognized commands - may report these in future
                console.log(`🔍 EXECUTE DEBUG: UNRECOGNIZED command type: "${command.type}"`);
                try { log(`Actor Channel: Unrecognized command type: ${command.type}`); } catch(e) {}
        }
    } finally {
        // Clear Actor flag after longer delay to catch all related DOM events
        setTimeout(() => {
            log(`Actor Channel: Clearing actorExecuting flag after 500ms delay`);
            window.actorExecuting = false;
        }, 500);
    }
}

// Echo function removed - rely on natural Observer events with proper source attribution

// ========================================================================
// ACTOR CHANNEL INITIALIZATION
// ========================================================================

/**
 * Start Actor channel polling when content script loads
 * Runs in background, non-blocking
 */
function initializeActorChannel() {
    log('Actor Channel: Initializing Actor command polling');

    // Start polling in background (don't await - let it run continuously)
    pollForActorCommands().catch(error => {
        log(`Actor Channel: Polling loop crashed: ${error.message}`);
        // Could implement restart logic here if needed
    });
}

// Initialize Actor channel when content script loads
initializeActorChannel();

// Debug: Verify event listeners are attached
log('CONTENT SCRIPT VERSION 2025-07-13-00:40 LOADED');
// sendEvent('log', { message: 'Content script loaded successfully', version: '2025-07-13-00:40' });
//
// // Test if basic event sending works
// sendEvent('log', { message: 'Testing basic event sending functionality' });
//
// // Test if click listener attachment works
// log('Adding click listener...');
// sendEvent('log', { message: 'About to add click event listener' });
//
// // Removed synthetic click test - it was cluttering the real data
//
