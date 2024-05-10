function formatDate(year, month, day) {
    const date = new Date(year, month - 1, day); // Month is 0-indexed in JavaScript Date
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

module.exports = {
    formatDate
};
