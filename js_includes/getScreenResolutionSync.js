const si = require('systeminformation');
const deasync = require('deasync');

function getScreenResolutionSync() {
    let done = false;
    let screenWidth = 0;
    let screenHeight = 0;
    let errorOccurred = null;

    // Asynchronously fetch graphics information
    si.graphics().then(data => {
        if (data && data.displays && data.displays.length > 0) {
            screenWidth = data.displays[0].resolutionX;
            screenHeight = data.displays[0].resolutionY;
        }
        done = true;
    }).catch(error => {
        console.error("Error fetching screen information:", error);
        errorOccurred = error;
        done = true;
    });

    // Wait here until the asynchronous call completes
    deasync.loopWhile(() => !done);

    if (errorOccurred) {
        throw errorOccurred;
    }

    return { screenWidth, screenHeight };
}

module.exports = {
    getScreenResolutionSync
};
