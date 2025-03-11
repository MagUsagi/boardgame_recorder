document.getElementById('random-game-btn').addEventListener('click', function() {
    const display = document.getElementById('random-game-title');
    const image = document.getElementById('random-game-image');
    const games = JSON.parse(document.getElementById('games-data').textContent);

    let count = 0;
    const interval = setInterval(() => {
        const randomIndex = Math.floor(Math.random() * games.length);
        const game = games[randomIndex];
        display.textContent = game.title;
        display.setAttribute('href', game.url);
        image.style.backgroundImage = game.image;

        count++;
        if (count > 20) { // 20回表示したらストップ
            clearInterval(interval);
            
            // 最後に1回だけランダムに決定する
            const finalIndex = Math.floor(Math.random() * games.length);
            const finalGame = games[finalIndex];
            display.textContent = finalGame.title;
            display.setAttribute('href', finalGame.url);
            image.style.backgroundImage = finalGame.image;
        }
    }, 100);
});
