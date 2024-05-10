const fs = require('fs');

async function readConfig(configPath) {
    const data = await fs.promises.readFile(configPath);
    return JSON.parse(data);
}

async function writeConfig(configPath, config) {
    await fs.promises.writeFile(configPath, JSON.stringify(config, null, 2));
}

module.exports = {
    readConfig, writeConfig
};
