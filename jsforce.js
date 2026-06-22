const SALESFORCE_SERVER_URL = 'https://orgcs.my.salesforce.com';

function getCookie(url, name) {
  return new Promise((resolve) => {
    chrome.cookies.get({ url, name }, function (cookie) {
      resolve(cookie || null);
    });
  });
}

async function getSessionId() {
  const cookie = await getCookie(SALESFORCE_SERVER_URL, 'sid');
  if (cookie && cookie.value) {
    console.log('[SF Session] Found session cookie at', SALESFORCE_SERVER_URL);
    return cookie.value;
  }
  throw new Error('No Salesforce session. Please log in to OrgCS.');
}

function createSalesforceConnection(sessionId, version) {
  if (!sessionId || typeof jsforce === 'undefined') {
    throw new Error('Session ID or jsforce library not available');
  }
  return new jsforce.Connection({
    serverUrl: SALESFORCE_SERVER_URL,
    sessionId: sessionId,
    version: version || SF_API_VERSION
  });
}
