/* global ClipboardJS, discordAnnouncementsSettings */

$(document).ready(() => {
    'use strict';

    /* Variables
    --------------------------------------------------------------------------------- */
    // Selects
    const selectAnnouncementTarget = $('select#id_announcement_target');
    const selectAnnouncementChannel = $('select#id_announcement_channel');

    // Input fields
    const inputCsrfMiddlewareToken = $('input[name="csrfmiddlewaretoken"]');
    const inputAnnouncementText = $('textarea[name="announcement_text"]');

    // Form
    const announcementForm = $('#aa-discord-announcements-form');

    /* Functions
    --------------------------------------------------------------------------------- */
    /**
     * Checks if the given item is a plain object, excluding arrays and dates.
     *
     * @param {*} item - The item to check.
     * @returns {boolean} True if the item is a plain object, false otherwise.
     */
    const isObject = (item) => {
        return (
            item && typeof item === 'object' && !Array.isArray(item) && !(item instanceof Date)
        );
    };

    /**
     * Fetch data from an ajax URL
     *
     * Do not call this function directly, use fetchGet or fetchPost instead.
     *
     * @param {string} url The URL to fetch data from
     * @param {string} method The HTTP method to use for the request (default: 'get')
     * @param {string|null} csrfToken The CSRF token to include in the request headers (default: null)
     * @param {string|null} payload The payload (JSON|Object) to send with the request (default: null)
     * @param {boolean} responseIsJson Whether the response is expected to be JSON or not (default: true)
     * @returns {Promise<string>} The fetched data
     * @throws {Error} Throws an error when:
     * - The method is not valid (only `get` and `post` are allowed).
     * - The CSRF token is required but not provided for POST requests.
     * - The payload is not an object when using POST method.
     * - The response status is not OK (HTTP 200-299).
     * - There is a network error or if the response cannot be parsed as JSON.
     */
    const _fetchAjaxData = async ({
        url,
        method = 'get',
        csrfToken = null,
        payload = null,
        responseIsJson = true
    }) => {
        const normalizedMethod = method.toLowerCase();

        // Validate the method
        const validMethods = ['get', 'post'];

        if (!validMethods.includes(normalizedMethod)) {
            throw new Error(`Invalid method: ${method}. Valid methods are: get, post`);
        }

        const headers = {};

        // Set headers based on response type
        if (responseIsJson) {
            headers['Accept'] = 'application/json'; // jshint ignore:line
            headers['Content-Type'] = 'application/json';
        }

        let requestUrl = url;
        let body = null;

        if (normalizedMethod === 'post') {
            if (!csrfToken) {
                throw new Error('CSRF token is required for POST requests');
            }

            headers['X-CSRFToken'] = csrfToken;

            if (payload !== null && !isObject(payload)) {
                throw new Error('Payload must be an object when using POST method');
            }

            body = payload ? JSON.stringify(payload) : null;
        } else if (normalizedMethod === 'get' && payload) {
            const queryParams = new URLSearchParams(payload).toString(); // jshint ignore:line

            requestUrl += (url.includes('?') ? '&' : '?') + queryParams;
        }

        try {
            const response = await fetch(requestUrl, {
                method: method.toUpperCase(),
                headers: headers,
                body: body
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            return responseIsJson ? await response.json() : await response.text();
        } catch (error) {
            console.log(`Error: ${error.message}`);

            throw error;
        }
    };

    /**
     * Fetch data from an ajax URL using the GET method.
     * This function is a wrapper around _fetchAjaxData to simplify GET requests.
     *
     * @param {string} url The URL to fetch data from
     * @param {string|null} payload The payload (JSON) to send with the request (default: null)
     * @param {boolean} responseIsJson Whether the response is expected to be JSON or not (default: true)
     * @return {Promise<string>} The fetched data
     */
    const fetchGet = ({
        url,
        payload = null,
        responseIsJson = true
    }) => {
        return _fetchAjaxData({
            url: url,
            method: 'get',
            payload: payload,
            responseIsJson: responseIsJson
        });
    };

    /**
     * Fetch data from an ajax URL using the POST method.
     * This function is a wrapper around _fetchAjaxData to simplify POST requests.
     * It requires a CSRF token for security purposes.
     *
     * @param {string} url The URL to fetch data from
     * @param {string|null} csrfToken The CSRF token to include in the request headers (default: null)
     * @param {string|null} payload The payload (JSON) to send with the request (default: null)
     * @param {boolean} responseIsJson Whether the response is expected to be JSON or not (default: true)
     * @return {Promise<string>} The fetched data
     */
    const fetchPost = ({
        url,
        csrfToken,
        payload = null,
        responseIsJson = true
    }) => {
        return _fetchAjaxData({
            url: url,
            method: 'post',
            csrfToken: csrfToken,
            payload: payload,
            responseIsJson: responseIsJson
        });
    };

    /**
     * Get the additional Discord ping targets for the current user
     */
    const getAnnouncementTargetsForCurrentUser = () => {
        fetchGet({
            url: discordAnnouncementsSettings.url.getAnnouncementTargets,
            responseIsJson: false
        }).then((announcementTargets) => {
            if (announcementTargets !== '') {
                $(selectAnnouncementTarget).html(announcementTargets);
            }
        }).catch((error) => {
            console.error('Error fetching announcement targets:', error);
        });
    };

    /**
     * Get webhooks for current user
     */
    const getWebhooksForCurrentUser = () => {
        fetchGet({
            url: discordAnnouncementsSettings.url.getAnnouncementWebhooks,
            responseIsJson: false
        }).then((announcementWebhooks) => {
            if (announcementWebhooks !== '') {
                $(selectAnnouncementChannel).html(announcementWebhooks);
            }
        }).catch((error) => {
            console.error('Error fetching announcement webhooks:', error);
        });
    };

    /**
     * Closing the message
     *
     * @param {string} element
     * @param {int} closeAfter Close Message after given time in seconds (Default: 10)
     */
    const closeMessageElement = (element, closeAfter = 10) => {
        $(element).fadeTo(closeAfter * 1000, 500).slideUp(500, () => {
            $(element).remove();
        });
    };

    /**
     * Show a success message box
     *
     * @param {string} message
     * @param {string} element
     */
    const showSuccess = (message, element) => {
        $(element).html(
            `<div class="alert alert-success alert-dismissible alert-message-success d-flex align-items-center fade show">${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`
        );

        closeMessageElement('.alert-message-success');
    };

    /**
     * Show an error message box
     *
     * @param {string} message
     * @param {string} element
     */
    const showError = (message, element) => {
        $(element).html(
            `<div class="alert alert-danger alert-dismissible alert-message-error d-flex align-items-center fade show">${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`
        );

        closeMessageElement('.alert-message-error', 9999);
    };

    /**
     * Copy the fleet ping to clipboard
     */
    const copyAnnouncementText = () => {
        /**
         * Copy text to clipboard
         *
         * @type Clipboard
         */
        const clipboardFleetPingData = new ClipboardJS('button#copyDiscordAnnouncement');

        /**
         * Copy success
         *
         * @param {type} e
         */
        clipboardFleetPingData.on('success', (e) => {
            showSuccess(
                discordAnnouncementsSettings.translation.copyToClipboard.success,
                '.aa-discord-announcements-announcement-copyresult'
            );

            e.clearSelection();
            clipboardFleetPingData.destroy();
        });

        /**
         * Copy error
         */
        clipboardFleetPingData.on('error', () => {
            showError(
                discordAnnouncementsSettings.translation.copyToClipboard.error,
                '.aa-discord-announcements-announcement-copyresult'
            );

            clipboardFleetPingData.destroy();
        });
    };

    /* Events
    --------------------------------------------------------------------------------- */
    /**
     * Generate announcement text
     */
    announcementForm.submit((event) => {
        // Stop the browser from sending the form, we take care of it
        event.preventDefault();

        // Close all possible form messages
        $('.aa-discord-announcements-form-message div').remove();

        // Check for mandatory fields
        const announcementFormMandatoryFields = [
            inputAnnouncementText.val()
        ];

        if (announcementFormMandatoryFields.includes('')) {
            showError(
                discordAnnouncementsSettings.translation.error.missingFields,
                '.aa-discord-announcements-form-message'
            );

            return false;
        }

        // Get the form data
        const formData = announcementForm.serializeArray().reduce((obj, item) => {
            obj[item.name] = item.value;

            return obj;
        }, {});

        // Fetch API call to create the announcement
        fetchPost({
            url: discordAnnouncementsSettings.url.createAnnouncement,
            csrfToken: inputCsrfMiddlewareToken.val(),
            payload: formData,
            responseIsJson: true
        }).then((data) => {
            if (data.success === true) {
                $('.aa-discord-announcements-no-announcement').hide('fast');
                $('.aa-discord-announcements-announcement').show('fast');
                $('.aa-discord-announcements-announcement-text')
                    .html(data.announcement_context);

                if (data.message) {
                    showSuccess(
                        data.message,
                        '.aa-discord-announcements-form-message'
                    );
                }
            } else {
                showError(
                    data.message || 'Something went wrong, no details given.',
                    '.aa-discord-announcements-form-message'
                );
            }
        }).catch((error) => {
            console.error(`Error: ${error.message}`);

            showError(
                error.message || 'Something went wrong, no details given.',
                '.aa-discord-announcements-form-message'
            );
        });
    });

    /**
     * Copy ping text
     */
    $('button#copyDiscordAnnouncement').on('click', () => {
        copyAnnouncementText();
    });

    /**
     * Initialize functions that need to start on load
     */
    (() => {
        getAnnouncementTargetsForCurrentUser();
        getWebhooksForCurrentUser();
    })();
});
