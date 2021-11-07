fetch('https://api.github.com/repos/isaacKenyon/VALORANT-rank-yoinker/releases')
    .then(response => response.json())
    .then(data => console.log(data));



