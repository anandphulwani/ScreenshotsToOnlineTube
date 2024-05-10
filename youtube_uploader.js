async function waitForXPathElement(page, xpathExpression) {
    await page.waitForFunction(xpath => {
        const iterator = document.evaluate(xpath, document, null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null );
        return iterator.iterateNext();
    }, {}, xpathExpression);
}

// const puppeteer = require('puppeteer');
const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const AnonymizeUAPlugin = require("puppeteer-extra-plugin-anonymize-ua");
const AdblockerPlugin = require("puppeteer-extra-plugin-adblocker");

puppeteer.use(StealthPlugin());
puppeteer.use(AnonymizeUAPlugin());
puppeteer.use(
    AdblockerPlugin({
        blockTrackers: true,
    })
);

const fs = require('fs').promises;
const path = require('path');

// Configuration and paths
const configPath = '.\\configs\\config.json'; // Your config file path
const chromiumPath = '.\\bin\\chrome-win\\x64\\chrome.exe'; // Path to your Chromium executable
const playlistName = process.argv[2]; // Playlist name passed as argument
const videoPath = process.argv[3]; // Video file path passed as argument

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function readConfig() {
    const data = await fs.readFile(configPath);
    return JSON.parse(data);
}

async function writeConfig(config) {
    await fs.writeFile(configPath, JSON.stringify(config, null, 2));
}

async function main() {
    try {
        const config = await readConfig();

        if (!config.playing) {
            // const browser = await puppeteer.launch({
            //     headless: false, // Set to false to see the browser actions
            //     executablePath: chromiumPath,
            // });

            const browser = await puppeteer.launch({
                headless: false,
                executablePath: chromiumPath,
                defaultViewport: null,
                ignoreDefaultArgs: ["--disable-extensions"],
                args: [
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--user-data-dir=${path.join(__dirname, 'dev - user - data')}",
                ],
            });
            // const page = await browser.newPage();
            const pages = await browser.pages();
            const page = pages[0];
            await page.goto('https://studio.youtube.com/');

            await page.waitForSelector('input[autocomplete="username"]');
            await page.type('input[autocomplete="username"]', 'harlax.monitoring@gmail.com');
            await page.waitForSelector('#identifierNext button');
            await page.click('#identifierNext button');

            await page.waitForSelector('#password');
            await page.evaluate(() => { const element = document.querySelector('#password'); });
            // const elementInnerHTML = await page.evaluate(() => {
            //     const element = document.querySelector('#password');
            //     return element ? element.outerHTML : null;
            // });
            // console.log(elementInnerHTML);

            await page.waitForSelector('#password input[type="password"]');
            await page.click('#password input[type="password"]');
            await page.type('#password input[type="password"]', 'zcfybeng268re');

            await page.waitForSelector('#passwordNext button');
            await sleep(1500);

            await page.click('#passwordNext button');
            await page.waitForSelector('#create-icon');
            await page.click('#create-icon');
            await page.waitForSelector('[test-id="upload-beta"]');
            await page.click('[test-id="upload-beta"]');

            page.waitForSelector('#select-files-button');
            const [fileChooser] = await Promise.all([
                page.waitForFileChooser(),
                page.click('#select-files-button'),
            ]);
            await fileChooser.accept(['C:\\Users\\anand\\Desktop\\ScreensData\\CEO-PC1_2022_09_25.mp4']);

            console.log("001");
            const xpathMadeForKids = "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']//div[@id='onRadio']";
            await waitForXPathElement(page, xpathMadeForKids);
            console.log("002");
            const [onRadioElementMadeForKids] = await page.$x(xpathMadeForKids);
            console.log("003");
            if (onRadioElementMadeForKids) {
                await onRadioElementMadeForKids.click();
            } else {
                console.log('Element `VIDEO_MADE_FOR_KIDS_NOT_MFK` not found');
                process.exit(1);
            }
            console.log("004");

            console.log("005");
            const toggleXPathShowMoreShowLess = "//div[contains(@class, 'toggle-section')]//div[@id='toggle-button']//div[contains(@class, 'label') and text()='Show more']";
            await waitForXPathElement(page, toggleXPathShowMoreShowLess);

            console.log("006");
            const [toggleButtonShowMoreShowLess] = await page.$x(toggleXPathShowMoreShowLess);
            if (toggleButtonShowMoreShowLess) {
                await toggleButtonShowMoreShowLess.click();
            } else {
                throw new Error("Toggle ShowMore-ShowLess button not found.");
            }
            console.log("007");

            // Wait for the text to change to "Show less"
            await page.waitForFunction(
                () => {
                    const el = document.querySelector("div.toggle-section #toggle-button .label");
                    return el && el.textContent.trim() === "Show less";
                },
                { timeout: 5000 }
            );
            console.log("008");

            console.log('Text has changed to "Show less".');

            console.log("Done");

            await sleep(50000);

            // await page.waitForNavigation({ waitUntil: 'networkidle0' });

            // // Wait for the "buttons" div to be loaded
            // await page.waitForSelector('#buttons');

            // // Using XPath to find the <a> element that is a descendant of a div with id "buttons" and follows a <yt-button-shape>
            // const linkXPath = "//div[@id='buttons']//yt-button-shape/following-sibling::*//a";

            // // Evaluate the XPath expression to get the element handle
            // const links = await page.$x(linkXPath);

            // if (links.length > 0) {
            // // Assuming you want to click the first link that matches
            // await links[0].click();
            // console.log("Clicked on the <a> link inside #buttons div, following <yt-button-shape>");
            // } else {
            // console.log("No <a> link found inside #buttons div, following <yt-button-shape>");
            // }

            await sleep(5000);

            // Check for playlist existence and create if it doesn't exist
            // Note: Implement the logic to check the playlist and create one if it doesn't exist
            // Update config if playlist exists
            // await checkOrCreatePlaylist(page, playlistName);

            // Go to video upload section and upload video
            // Note: Implement the logic for video upload and setting options including adding to playlist
            // await uploadVideoAndAddToPlaylist(page, videoPath, playlistName);

            // await browser.close();
            // Update config
            config.playing = true; // Or any other logic you applied
            await writeConfig(config);
        } else {
            console.log("Config 'playing' is already set to true. Exiting.");
        }
    } catch (error) {
        console.error("An error occurred: ", error.message);
        if (error.name === 'TimeoutError') {
            console.error("Operation timed out.");
        }
        process.exit(1);
    } finally {
        if (browser) {
            await browser.close();
        }
    }

}

main().catch(console.error);
