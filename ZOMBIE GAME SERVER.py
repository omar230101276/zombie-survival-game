from socket import *
import os

# Define server address and port
serverIP = '192.168.1.8'
serverPort = 6789
serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind the socket to the specific IP address and port
serverSocket.bind((serverIP, serverPort))

# Listen for incoming connections (queue up to 1 connection)
serverSocket.listen(1)
print("The server is ready to receive on IP", serverIP, "port", serverPort)

# Define the HTML content to serve
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zombie Survival</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="game-container">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div id="score-board">Score: 0</div>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""

# Define the CSS content to serve
css_content = """
body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #000;
    font-family: Arial, sans-serif;
}

#game-container {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}

#gameCanvas {
    border: 1px solid #fff;
    background-color: #000;
}

#score-board {
    margin-top: 20px;
    font-size: 24px;
    color: #fff;
}
"""

# Define the JavaScript content to serve
js_content = """
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreBoard = document.getElementById('score-board');
let score = 0;
let gameInterval, zombieIntervalId;

const player = {
    x: canvas.width / 2 - 15,
    y: canvas.height / 2 - 15,
    width: 30,
    height: 30,
    dx: 0,
    dy: 0,
};

const zombies = [];
const zombieSpeed = 1;
const zombieInterval = 2000;

function drawPlayer() {
    ctx.fillStyle = '#00f';
    ctx.fillRect(player.x, player.y, player.width, player.height);
}

function drawZombie(zombie) {
    ctx.fillStyle = '#0f0';
    ctx.fillRect(zombie.x, zombie.y, zombie.width, zombie.height);
}

function movePlayer() {
    player.x += player.dx;
    player.y += player.dy;
    if (player.x < 0) player.x = 0;
    if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;
    if (player.y < 0) player.y = 0;
    if (player.y + player.height > canvas.height) player.y = canvas.height - player.height;
}

function createZombie() {
    const x = Math.random() < 0.5 ? 0 : canvas.width - 30;
    const y = Math.random() * canvas.height;
    const zombie = { x, y, width: 30, height: 30 };
    zombies.push(zombie);
}

function moveZombies() {
    zombies.forEach((zombie, index) => {
        const angle = Math.atan2(player.y - zombie.y, player.x - zombie.x);
        zombie.x += Math.cos(angle) * zombieSpeed;
        zombie.y += Math.sin(angle) * zombieSpeed;
        if (
            zombie.x < player.x + player.width &&
            zombie.x + zombie.width > player.x &&
            zombie.y < player.y + player.height &&
            zombie.height + zombie.y > player.y
        ) {
            clearInterval(gameInterval);
            clearInterval(zombieIntervalId);
            alert('Game Over! Your score is ' + score);
            document.location.reload();
        }
    });
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function gameLoop() {
    clearCanvas();
    drawPlayer();
    movePlayer();
    moveZombies();
    zombies.forEach(drawZombie);
    score++;
    scoreBoard.innerText = 'Score: ' + score;
}

function startGame() {
    gameInterval = setInterval(gameLoop, 1000 / 60);
    zombieIntervalId = setInterval(createZombie, zombieInterval);
}

// Handle keyboard input
document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowUp') {
        player.dy = -3;
    } else if (event.key === 'ArrowDown') {
        player.dy = 3;
    } else if (event.key === 'ArrowLeft') {
        player.dx = -3;
    } else if (event.key === 'ArrowRight') {
        player.dx = 3;
    }
});

document.addEventListener('keyup', (event) => {
    if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
        player.dy = 0;
    } else if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        player.dx = 0;
    }
});

// Start the game
startGame();
"""

while True:
    # Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    try:
        # Receive the request message from the client
        message = connectionSocket.recv(1024).decode()
        if not message:
            connectionSocket.close()
            continue

        # Extract the path of the requested file from the message
        filename = message.split()[1][1:]
        print(f"Requested file: {filename}")

        # Check if the requested file is the embedded HTML
        if filename == "" or filename == "index.html":
            # Send HTTP response header
            connectionSocket.sendall("HTTP/1.1 200 OK\r\n".encode())
            connectionSocket.sendall("Content-Type: text/html\r\n".encode())
            connectionSocket.sendall("\r\n".encode())
            
            # Send the content of the embedded HTML to the client
            connectionSocket.sendall(html_content.encode())
        elif filename == "styles.css":
            # Send HTTP response header
            connectionSocket.sendall("HTTP/1.1 200 OK\r\n".encode())
            connectionSocket.sendall("Content-Type: text/css\r\n".encode())
            connectionSocket.sendall("\r\n".encode())
            
            # Send the content of the CSS to the client
            connectionSocket.sendall(css_content.encode())
        elif filename == "script.js":
            # Send HTTP response header
            connectionSocket.sendall("HTTP/1.1 200 OK\r\n".encode())
            connectionSocket.sendall("Content-Type: application/javascript\r\n".encode())
            connectionSocket.sendall("\r\n".encode())
            
            # Send the content of the JavaScript to the client
            connectionSocket.sendall(js_content.encode())
        else:
            # Check if the file exists
            if os.path.isfile(filename):
                # Read the file content
                with open(filename, 'rb') as f:
                    file_content = f.read()

                # Send HTTP response header
                connectionSocket.sendall("HTTP/1.1 200 OK\r\n".encode())
                connectionSocket.sendall("Content-Type: text/html\r\n".encode())
                connectionSocket.sendall("\r\n".encode())
                
                # Send the content of the requested file to the client
                connectionSocket.sendall(file_content)
            else:
                # Send 404 Not Found response
                connectionSocket.sendall("HTTP/1.1 404 Not Found\r\n".encode())
                connectionSocket.sendall("Content-Type: text/html\r\n".encode())
                connectionSocket.sendall("\r\n".encode())
                connectionSocket.sendall("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        
        # Close the client connection socket
        connectionSocket.close()
    except Exception as e:
        print(f"Error: {e}")
        # Send response message for internal server error
        connectionSocket.sendall("HTTP/1.1 500 Internal Server Error\r\n".encode())
        connectionSocket.sendall("Content-Type: text/html\r\n".encode())
        connectionSocket.sendall("\r\n".encode())
        connectionSocket.sendall("<html><body><h1>500 Internal Server Error</h1></body></html>\r\n".encode())
        
        # Close the client connection socket
        connectionSocket.close()

serverSocket.close()
