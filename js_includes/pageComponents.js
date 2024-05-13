const { sleep } = require('./sleep');

async function clickOnUploadButton(page) {
    await page.waitForSelector('#create-icon', { timeout: 5 * 60 * 1000 });
    await page.click('#create-icon');
    await sleep(3 * 1000);

    await page.waitForSelector('[test-id="upload-beta"]', { timeout: 5 * 60 * 1000 });
    await page.click('[test-id="upload-beta"]');
    await sleep(3 * 1000);
}

async function browseButtonAndSelectFileToUpload(page, normalizedFilePath) {
    page.waitForSelector('#select-files-button', { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    const [fileChooser] = await Promise.all([
        page.waitForFileChooser(),
        page.click('#select-files-button'),
    ]);
    await fileChooser.accept([normalizedFilePath]);
}

async function clickOnVideoMadeNotForKids(page) {
    const xpathDetails = "//*[@id='details']";
    await page.waitForSelector(`::-p-xpath(${xpathDetails})`, { timeout: 5 * 60 * 1000 });

    const xpathMadeForKids = "//*[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']//div[@id='radioContainer']";
    const onRadioElementMadeForKids = await page.waitForSelector(`::-p-xpath(${xpathMadeForKids})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (onRadioElementMadeForKids) {
        await onRadioElementMadeForKids.click();
    } else {
        console.log('Element `VIDEO_MADE_FOR_KIDS_NOT_MFK` not found');
        process.exit(1);
    }
}

async function clickOnShowMoreShowLess(page) {
    const toggleXPathShowMoreShowLess = "//div[contains(@class, 'toggle-section')]//*[@id='toggle-button']//div[contains(@class, 'label') and text()='Show more']";
    const toggleButtonShowMoreShowLess = await page.waitForSelector(`::-p-xpath(${toggleXPathShowMoreShowLess})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (toggleButtonShowMoreShowLess) {
        await toggleButtonShowMoreShowLess.click();
    } else {
        throw new Error("Toggle ShowMore-ShowLess button not found.");
    }

    await page.waitForFunction( // Wait for the text to change to "Show less"
        () => {
            const el = document.querySelector("div.toggle-section #toggle-button .label");
            return el && el.textContent.trim() === "Show less";
        },
        { timeout: 5000 }
    );
}

async function clickOnAllowAutomaticPlaces(page) {
    // const xpathAllowAutomaticPlaces = "//*[@id='has-autoplaces-mentioned-checkbox']//div[@id='checkbox-container']";
    const xpathAllowAutomaticPlaces = "//div[contains(text(), 'Allow automatic concepts')]/ancestor::div[@id='root-container']//div[@id='checkbox-container']";
    const onCheckboxAllowAutomaticPlaces = await page.waitForSelector(`::-p-xpath(${xpathAllowAutomaticPlaces})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (onCheckboxAllowAutomaticPlaces) {
        await onCheckboxAllowAutomaticPlaces.click();
    } else {
        console.log('Element `has-autoplaces-mentioned-checkbox` not found');
        process.exit(1);
    }
}

async function selectOrCreatePlaylist(page, playlist, privacystatus) {
    // Click on playlists dropdown
    const xpathYTCPPlaylists = "//ytcp-video-metadata-playlists";
    const playlistButton = await page.waitForSelector(`::-p-xpath(${xpathYTCPPlaylists})`, { timeout: 5 * 60 * 1000 });
    if (playlistButton) {
        await playlistButton.click();
    } else {
        console.log('Element `ytcp-video-metadata-playlists` not found');
        process.exit(1);
    }

    let createPlaylist = false;
    do {
        try {        
            // Wait for Playlist List to open up
            const xpathBlankItems = "//*[@id='playlists-list']//div[contains(concat(' ', normalize-space(@class), ' '), ' no-items-message ')]";
            const elementExists = await page.evaluate((xpath) => {
                const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                return result.singleNodeValue !== null;
            }, xpathBlankItems);
            if (elementExists) {
                createPlaylist = true
                break
            }

            const xpathItems = "//*[@id='playlists-list']//div[@id='items']";
            const itemsContainer = await page.waitForSelector(`::-p-xpath(${xpathItems})`, { visible: true })
            const childCount = await page.evaluate(element => element.children.length, itemsContainer);
            if (childCount == 1)
            {
                createPlaylist = true
                break
            }

            const xpathInnerSpan = `//*[@id='playlists-list']//div[@id='items']//span[contains(concat(' ', normalize-space(@class), ' '), ' checkbox-label ')]//span[contains(text(), '${playlist}')]`;
            try {
                await page.waitForSelector(`::-p-xpath(${xpathInnerSpan})`, { timeout: 5000 }, { timeout: 5 * 60 * 1000 });
                const xpathPrecedingSibling = `${xpathInnerSpan}/../preceding-sibling::*[1]`;
                const selectPlaylistCheckbox = await page.waitForSelector(`::-p-xpath(${xpathPrecedingSibling})`, { timeout: 5 * 60 * 1000 });
                if (selectPlaylistCheckbox) {
                    await selectPlaylistCheckbox.click();
                    await page.waitForFunction(
                        (element) => element.getAttribute('aria-checked') === 'true',
                        { timeout: 5000 },
                        selectPlaylistCheckbox
                    );
                } else {
                    console.log('Playlist selection checkbox not found.');
                    process.exit(1);
                }
            } catch (error) {
                if (error.name === 'TimeoutError') {
                    createPlaylist = true
                    break
                } else {
                    throw error;
                }
            }
        } catch (error) {
            console.error("Error finding the element or evaluating it:", error);
        }
    } while (false)

    if (createPlaylist) 
    {
        const xpathCreatePlaylistDropDown = "//ytcp-button[contains(concat(' ', normalize-space(@class), ' '), ' new-playlist-button ')]";
        const createPlaylistDropDown = await page.waitForSelector(`::-p-xpath(${xpathCreatePlaylistDropDown})`, { visible: true }, { timeout: 5 * 60 * 1000 });
        await sleep(3 * 1000);

        if (!createPlaylistDropDown) {
            throw new Error("Create playlist dropdown not found.");
        }
        await createPlaylistDropDown.click();
        const xpathCreatePlaylistButton = "//tp-yt-paper-item[@test-id='new_playlist']";
        const createPlaylistButton = await page.waitForSelector(`::-p-xpath(${xpathCreatePlaylistButton})`, { visible: true }, { timeout: 5 * 60 * 1000 });
        await sleep(3 * 1000);

        if (!createPlaylistButton) {
            throw new Error("Create playlist button not found.");
        }
        await createPlaylistButton.click();

        const xpathPlaylistTitle = "//ytcp-playlist-metadata-editor//*[@id='title-textarea']//div[@id='child-input']";
        const playlistTitle = await page.waitForSelector(`::-p-xpath(${xpathPlaylistTitle})`, { visible: true }, { timeout: 5 * 60 * 1000 });
        await playlistTitle.click();
        await sleep(3 * 1000);

        await page.keyboard.type(playlist);
        await sleep(3 * 1000);

        const xpathPlaylistPrivacyStatus = "//ytcp-playlist-metadata-editor//*[@id='visibility-selector']//ytcp-dropdown-trigger";
        const playlistPrivacyStatus = await page.waitForSelector(`::-p-xpath(${xpathPlaylistPrivacyStatus})`, { visible: true }, { timeout: 5 * 60 * 1000 });
        await playlistPrivacyStatus.click();
        await sleep(3 * 1000);

        let xpathPlaylistPrivacyStatusSelection = "//ytcp-playlist-metadata-editor//ytcp-text-menu[@id='visibility-menu']//tp-yt-paper-listbox[@id='paper-list']";
        xpathPlaylistPrivacyStatusSelection += `//*[@role='option' and @test-id='${privacystatus.toUpperCase()}']`;
        const playlistPrivacyStatusSelection = await page.waitForSelector(`::-p-xpath(${xpathPlaylistPrivacyStatusSelection})`, { visible: true }, { timeout: 5 * 60 * 1000 });
        await playlistPrivacyStatusSelection.click();
        await sleep(3 * 1000);

        try {
            const checkPrivacyStatus = "//ytcp-playlist-metadata-editor//div[contains(concat(' ', normalize-space(@class), ' '), ' visibility ')]//ytcp-text-dropdown-trigger[1]//ytcp-dropdown-trigger[1]//div[1]/div[2]/span[1]"
            await page.waitForSelector(`::-p-xpath(${checkPrivacyStatus})`, { visible: true })
            await page.waitForFunction(
                (xpath, privacystatus) => {
                    const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    return element !== null && element.innerText.toUpperCase() === privacystatus.toUpperCase();
                },
                { timeout: 5000 },
                checkPrivacyStatus, privacystatus
            );
        } catch (error) {
            console.error("Error:", error);
            process.exit(1)
        }

        const xpathCreateButton = "//ytcp-button[@id='create-button']//div[1]";
        const createButton = await page.waitForSelector(`::-p-xpath(${xpathCreateButton})`, { timeout: 5 * 60 * 1000 });
        await sleep(3 * 1000);
    
        if (createButton) {
            await createButton.click();
        } else {
            console.log('Element Create button not found');
            process.exit(1);
        }
    }

    try {
        const xpathDoneButton = "//ytcp-button[contains(concat(' ', normalize-space(@class), ' '), ' ytcp-playlist-dialog ') and @label='Done']"
        const playlistDoneButton = await page.waitForSelector(`::-p-xpath(${xpathDoneButton})`, { timeout: 5 * 60 * 1000 });
        if (playlistDoneButton) {
            await playlistDoneButton.click();
        } else {
            console.log('Element playlist done button not found.');
            process.exit(1);
        }

        const checkPlaylistLoaded = "//ytcp-video-metadata-playlists//ytcp-text-dropdown-trigger[1]//ytcp-dropdown-trigger[1]//div[1]/div[2]/span[1]"
        await page.waitForSelector(`::-p-xpath(${checkPlaylistLoaded})`, { visible: true })
        await page.waitForFunction(
            (xpath, playlist) => {
                const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                return element !== null && element.innerText === playlist;
            },
            { timeout: 5000 },
            checkPlaylistLoaded, playlist
        );
    } catch (error) {
        console.error("Error:", error);
        process.exit(1)
    }
}

async function clickNextButton(page) {
    const xpathNextBtn = "//ytcp-button[@id='next-button']//div[1]";
    const nextButton = await page.waitForSelector(`::-p-xpath(${xpathNextBtn})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (nextButton) {
        await nextButton.click();
    } else {
        console.log('Element Next button not found');
        process.exit(1);
    }
}

async function setPrivacyStatus(page, privacystatus) {
    const xpathPrivacyRadios = `//*[@id='privacy-radios']//*[@role='radio' and @name='${privacystatus.toUpperCase()}']`;
    const privacyRadioButton = await page.waitForSelector(`::-p-xpath(${xpathPrivacyRadios})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (privacyRadioButton) {
        await privacyRadioButton.click();
    } else {
        console.log('Element privacy radio button not found');
        process.exit(1);
    }
}

async function waitForUploadToComplete(page) {
    const xpathUploadingSection = '//ytcp-video-upload-progress/span[@class="progress-label style-scope ytcp-video-upload-progress"]';
    const uploadingSection = await page.waitForSelector(`::-p-xpath(${xpathUploadingSection})`, { timeout: 7200 * 1000 }, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (!uploadingSection) {
        console.log('Element uploading section not found');
        process.exit(1);
    }
    await page.waitForFunction(
        (xpath) => {
            const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            return element !== null && !element.innerHTML.startsWith('Uploading ');
        },
        { timeout: ( 7200 - 500 ) * 1000 },
        xpathUploadingSection
    );
    await sleep(5 * 1000);
}

async function clickSaveButton(page) {
    const xpathSaveBtn = "//ytcp-button[@id='done-button']//div[1]";
    const saveButton = await page.waitForSelector(`::-p-xpath(${xpathSaveBtn})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (saveButton) {
        await saveButton.click();
    } else {
        console.log('Element Save button not found');
        process.exit(1);
    }
}

async function clickCloseButton(page) {
    const xpathCloseBtn = "//ytcp-button[@id='close-button']//div[1]";
    const closeButton = await page.waitForSelector(`::-p-xpath(${xpathCloseBtn})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (closeButton) {
        await closeButton.click();
        await sleep(3 * 1000);
        return true;
    } else {
        console.log('Element Close button not found');
        process.exit(1);
    }
}

async function addOrModifyTitle(page, title) {
    const xpathTitle = "//*[@id='title-textarea']//*[@id='child-input']//div[@id='textbox']";
    const titleDiv = await page.waitForSelector(`::-p-xpath(${xpathTitle})`, { timeout: 5 * 60 * 1000 });
    if (titleDiv) {
        await titleDiv.click();
    } else {
        console.log('Element `title-textarea` not found');
        process.exit(1);
    }
    await sleep(3 * 1000);

    // Select all text: Ctrl+A
    await page.keyboard.down('Control');
    await page.keyboard.press('A');
    await page.keyboard.up('Control');
    await sleep(3 * 1000);

    await page.keyboard.press('Backspace');
    await sleep(3 * 1000);

    await page.keyboard.type(title);
    await sleep(3 * 1000);

    await page.evaluate(element => element.innerHTML, titleDiv);
}

async function addOrModifyDescription(page, description) {
    const xpathTitle = "//*[@id='description-wrapper']//*[@id='child-input']//div[@id='textbox']";
    const descriptionDiv = await page.waitForSelector(`::-p-xpath(${xpathTitle})`, { timeout: 5 * 60 * 1000 });
    await sleep(3 * 1000);

    if (descriptionDiv) {
        await descriptionDiv.click();
    } else {
        console.log('Element `description-wrapper` not found');
        process.exit(1);
    }
    await sleep(3 * 1000);

    // Select all text: Ctrl+A
    await page.keyboard.down('Control');
    await page.keyboard.press('A');
    await page.keyboard.up('Control');
    await sleep(3 * 1000);

    await page.keyboard.press('Backspace');
    await sleep(3 * 1000);

    await page.keyboard.type(description.replace(/\r\n/g, '\n'));
    await sleep(3 * 1000);

    await page.evaluate(element => element.innerHTML, descriptionDiv);
}

async function waitForHeading(page, heading) {
    const xpathHeading = `//tp-yt-paper-dialog[@id='dialog']//div[contains(concat(' ', normalize-space(@class), ' '), ' dialog-content ')]//h1`;
    const innerHTML = await page.evaluate((xpath) => {
        const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        return element ? element.innerHTML : null;
    }, xpathHeading);
    return heading === innerHTML;
}

async function checkForDailyLimitReached(page) {
    let xpathIsErrorBlock = "//tp-yt-paper-dialog[@id='dialog']//div[contains(concat(' ', normalize-space(@class), ' '), ' dialog-content ')]";
    xpathIsErrorBlock += "//div[@id='error-block']//p[@id='error-message']";
    const isErrorBlockInnerHTML = await page.evaluate((xpath) => {
        const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        return element ? element.innerHTML : null;
    }, xpathIsErrorBlock);
    if (isErrorBlockInnerHTML !== "Oops, something went wrong.") {
        return false;
    }

    let wait_index = 0;
    do {
        let xpathErrorShort = "//tp-yt-paper-dialog[@id='dialog']//div[contains(concat(' ', normalize-space(@class), ' '), ' dialog-content ')]";
        xpathErrorShort += "//div[contains(concat(' ', normalize-space(@class), ' '), ' error-short ')]";
        const innerHTML = await page.evaluate((xpath) => {
            const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            return element ? element.innerHTML : null;
        }, xpathErrorShort);
        if (innerHTML.trim() === "") {
            if (wait_index > 15) {
                break
            }
            wait_index += 1
            await sleep(1 * 1000);
            continue;
        }
        return innerHTML === "Daily upload limit reached";
    } while(true)
}

module.exports = {
    clickOnUploadButton,
    browseButtonAndSelectFileToUpload,
    clickOnVideoMadeNotForKids,
    clickOnShowMoreShowLess,
    clickOnAllowAutomaticPlaces,
    addOrModifyDescription,
    addOrModifyTitle,
    selectOrCreatePlaylist,
    clickNextButton,
    waitForUploadToComplete,
    clickSaveButton,
    clickCloseButton,
    setPrivacyStatus,
    waitForHeading,
    checkForDailyLimitReached
};
