/*jshint esversion: 6 */

// Download Counter
fetch('https://api.github.com/repos/zayKenyon/VALORANT-rank-yoinker/releases')
    .then(response => response.json())
    .then(data => process_data(data));

function process_data(data) {
    console.log(data);
    let downloads_count = 0;
    for (let i = 0; i < data.length; i++) {
        downloads_count += data[i].assets[0].download_count;
    }
    document.getElementById("downloads").innerHTML = "Total Downloads: " + downloads_count;
}
