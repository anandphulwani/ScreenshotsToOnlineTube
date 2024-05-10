const puppeteerExtra = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const AnonymizeUAPlugin = require("puppeteer-extra-plugin-anonymize-ua");
const AdblockerPlugin = require("puppeteer-extra-plugin-adblocker");

puppeteerExtra.use(StealthPlugin());
puppeteerExtra.use(AnonymizeUAPlugin());
puppeteerExtra.use(
    AdblockerPlugin({
        blockTrackers: true,
    })
);

const fs = require('fs');
const path = require('path');

// Configuration and paths
const configPath = '.\\configs\\config.json'; // Your config file path
const chromiumPath = '.\\bin\\chrome-win\\x64\\chrome.exe'; // Path to your Chromium executable
const username = process.argv[2]
const password = process.argv[3]
const playlist = process.argv[4]
const privacystatus = process.argv[5]
const basepath = process.argv[6]

const { readConfig, writeConfig } = require('./js_includes/readWriteConfig');
const { formatDate } = require('./js_includes/formatDate');
const { sleep } = require('./js_includes/sleep');
const { getScreenResolutionSync } = require('./js_includes/getScreenResolutionSync');
const { 
    clickOnUploadButton,
    browseButtonAndSelectFileToUpload,
    clickOnVideoMadeNotForKids,
    clickOnShowMoreShowLess,
    clickOnAllowAutomaticPlaces,
    addOrModifyTitle,
    addOrModifyDescription,
    selectOrCreatePlaylist,
    clickNextButton,
    clickSaveButton,
    clickCloseButton,
    setPrivacyStatus,
    waitForHeading,
    checkForDailyLimitReached
} = require('./js_includes/pageComponents');


let browser;
let wsEndpoint;

async function loginToYTStudio() {
    const { _, screenHeight } = getScreenResolutionSync();
    browser = await puppeteerExtra.launch({
        headless: false,
        executablePath: chromiumPath,
        defaultViewport: null,
        ignoreDefaultArgs: ["--disable-extensions"],
        args: [
            "--start-maximized",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--user-data-dir=${path.join(__dirname, 'dev - user - data')}",
            `--window-position=0,${screenHeight + 30}` 
        ],
    });
    wsEndpoint = browser.wsEndpoint();

    const pages = await browser.pages();
    const page = pages[0];
    await sleep(3 * 1000)
    await page.goto('https://studio.youtube.com/');

    await page.waitForSelector('input[autocomplete="username"]');
    await page.type('input[autocomplete="username"]', `${username}@gmail.com`);
    await page.waitForSelector('#identifierNext button');
    await page.click('#identifierNext button');

    await page.waitForSelector('#password');
    await page.evaluate(() => { document.querySelector('#password'); });

    await page.waitForSelector('#password input[type="password"]');
    await page.click('#password input[type="password"]');
    // console.log('Sleeping Now.')
    // await sleep(10000)
    // console.log('Sleeping Over.')
    await page.type('#password input[type="password"]', `${password}`);

    await page.waitForSelector('#passwordNext button');
    await sleep(1500);

    await page.click('#passwordNext button');
}

async function uploadFiles(normalizedFilePath, title, description) {
    const config = await readConfig(configPath);

    if (!config.playing) {
        if (!wsEndpoint) {
            console.log('WebSocket endpoint not available');
            return;
        }
        const browser = await puppeteerExtra.connect({
            // headless: false,
            // executablePath: chromiumPath,
            defaultViewport: null,
            // ignoreDefaultArgs: ["--disable-extensions"],
            // args: [
            //     "--start-maximized",
            //     "--no-sandbox",
            //     "--disable-setuid-sandbox",
            //     "--user-data-dir=${path.join(__dirname, 'dev - user - data')}",
            // ],
            browserWSEndpoint: wsEndpoint
        });
        const pages = await browser.pages();
        const page = pages[0];

        await clickOnUploadButton(page);
        await browseButtonAndSelectFileToUpload(page, normalizedFilePath);
        if (await checkForDailyLimitReached(page)) {
            console.log("Error: Daily upload limit reached.");
            process.exit(0);
        }

        await addOrModifyTitle(page, title);
        await addOrModifyDescription(page, description);
        await clickOnVideoMadeNotForKids(page);
        await clickOnShowMoreShowLess(page);
        // await clickOnAllowAutomaticPlaces(page);
        await selectOrCreatePlaylist(page, playlist, privacystatus);

        do {
            await clickNextButton(page);
            await sleep(3 * 1000)
        } while (!await waitForHeading(page, "Video elements"))
        do {
            await clickNextButton(page);
            await sleep(3 * 1000)
        } while (!await waitForHeading(page, "Checks"))
        do {
            await clickNextButton(page);
            await sleep(3 * 1000)
        } while (!await waitForHeading(page, "Visibility"))
        
        await setPrivacyStatus(page, privacystatus);
        await clickSaveButton(page);
        const returnValue = await clickCloseButton(page);
        if (returnValue) {
            // Remove file
            try {
                fs.unlinkSync(normalizedFilePath);
                fs.unlinkSync(normalizedFilePath.replace(/\.[^.]*$/, '') + '_chapters.txt');
            } catch (err) {
                console.error(err);
            }
        }
        await page.goto('https://studio.youtube.com/channel/');

        // await page.waitForNavigation({ waitUntil: 'networkidle0' });
        // await browser.close();
        // Update config
        config.playing = true; // Or any other logic you applied
        await writeConfig(configPath, config);
    } else {
        console.log("Config 'playing' is already set to true. Exiting.");
    }


}


(async () => {
    try {
        await loginToYTStudio() 
        console.log(`basepath: ${basepath}`);
        let files;
        try {
            files = fs.readdirSync(basepath, { withFileTypes: true });
        } catch (err) {
            console.error('Error reading directory:', err);
            process.exit(1);
        }
        for (const file of files) {
            if (file.isFile() && file.name.endsWith('.mp4')) {
                const match = file.name.match(/(.+)_(\d{4})_(\d{2})_(\d{2})(_mini)?\.mp4/);
                if (match) {
                    const [_, hostname, year, month, day, miniSuffix] = match;
                    const dateStr = formatDate(year, month, day);
                    const titleSuffix = miniSuffix ? " Mini" : "";
                    const title = `${hostname.charAt(0).toUpperCase() + hostname.slice(1)}: ${dateStr}${titleSuffix}`;

                    const filePath = path.join(basepath, file.name);
                    const normalizedFilePath = path.normalize(filePath);
                    
                    const chaptersFilePath = normalizedFilePath.replace('.mp4', '_chapters.txt');
                    const description = fs.readFileSync(chaptersFilePath, 'utf8');

                    console.log(`Found file: ${file.name}, Title: ${title}, Processing file: ${normalizedFilePath}`);
                    await uploadFiles(normalizedFilePath, title, description)
                }
            }
        }
        if (browser) {
            await browser.close();
        }
    } catch (error) {
        if (error.name === 'TimeoutError') {
            console.error("Operation timed out.");
        }
        console.error("An error occurred: ", error.message);
        if (browser) {
            await browser.close();
        }
        process.exit(1);
    }
})();
