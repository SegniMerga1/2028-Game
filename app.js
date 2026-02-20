const gridSize = 4;
const startTiles = 2;
const spawnValues = [2, 4, 8, 16, 32];

const gridEl = document.getElementById("grid");
const scoreEl = document.getElementById("score");
const bestEl = document.getElementById("best");
const overlayEl = document.getElementById("overlay");
const restartBtn = document.getElementById("restart");
const playAgainBtn = document.getElementById("play-again");

let grid = [];
let score = 0;
let best = 0;

const tileColors = {
  2: "#f5f5f5",
  4: "#ffd3b6",
  8: "#ffad60",
  16: "#ff8c42",
  32: "#ff6f61",
  64: "#ff3e4d",
  128: "#a78bfa",
  256: "#7c3aed",
  512: "#4f46e5",
  1024: "#4338ca",
  2048: "#1d4ed8",
};

function initGame() {
  if (!gridEl || !scoreEl || !bestEl || !overlayEl || !restartBtn || !playAgainBtn) {
    // Basic guard if the DOM is not ready or elements are missing.
    return;
  }
  grid = Array.from({ length: gridSize }, () => Array(gridSize).fill(0));
  score = 0;
  overlayEl.hidden = true;
  for (let i = 0; i < startTiles; i += 1) {
    addTile();
  }
  render();
}

function addTile() {
  const empty = [];
  grid.forEach((row, r) => {
    row.forEach((value, c) => {
      if (value === 0) {
        empty.push({ r, c });
      }
    });
  });
  if (empty.length === 0) {
    return;
  }
  const { r, c } = empty[Math.floor(Math.random() * empty.length)];
  grid[r][c] = spawnValues[Math.floor(Math.random() * spawnValues.length)];
}

function render() {
  gridEl.innerHTML = "";
  grid.forEach((row) => {
    row.forEach((value) => {
      const tile = document.createElement("div");
      tile.className = "tile";
      if (value !== 0) {
        tile.textContent = value;
        tile.style.background = tileColors[value] || "#38bdf8";
        tile.style.color = value >= 128 ? "#0f172a" : "#0a0a0a";
        tile.classList.add("spawn");
      }
      gridEl.appendChild(tile);
    });
  });
  scoreEl.textContent = score;
  best = Math.max(best, score);
  bestEl.textContent = best;
}

function compress(row) {
  const filtered = row.filter((val) => val !== 0);
  while (filtered.length < gridSize) {
    filtered.push(0);
  }
  return filtered;
}

function merge(row) {
  let gained = 0;
  for (let i = 0; i < gridSize - 1; i += 1) {
    if (row[i] !== 0 && row[i] === row[i + 1]) {
      row[i] *= 2;
      row[i + 1] = 0;
      gained += row[i];
    }
  }
  return gained;
}

function moveLeft() {
  let moved = false;
  let gained = 0;
  const newGrid = grid.map((row) => {
    const compressed = compress(row);
    const rowGain = merge(compressed);
    const mergedRow = compress(compressed);
    if (!arraysEqual(row, mergedRow)) {
      moved = true;
    }
    gained += rowGain;
    return mergedRow;
  });
  return { newGrid, moved, gained };
}

function rotateGrid(direction) {
  let rotated = grid.map((row) => row.slice());
  const rotations = {
    right: 2,
    up: 1,
    down: 3,
  };
  const turns = rotations[direction] || 0;
  for (let t = 0; t < turns; t += 1) {
    rotated = rotated[0].map((_, i) => rotated.map((row) => row[i]).reverse());
  }
  return rotated;
}

function setGrid(newGrid, direction) {
  let rotated = newGrid.map((row) => row.slice());
  const rotations = {
    right: 2,
    up: 3,
    down: 1,
  };
  const turns = rotations[direction] || 0;
  for (let t = 0; t < turns; t += 1) {
    rotated = rotated[0].map((_, i) => rotated.map((row) => row[i]).reverse());
  }
  grid = rotated;
}

function arraysEqual(a, b) {
  return a.every((val, idx) => val === b[idx]);
}

function canMove() {
  if (grid.some((row) => row.includes(0))) {
    return true;
  }
  for (let r = 0; r < gridSize; r += 1) {
    for (let c = 0; c < gridSize - 1; c += 1) {
      if (grid[r][c] === grid[r][c + 1]) {
        return true;
      }
    }
  }
  for (let c = 0; c < gridSize; c += 1) {
    for (let r = 0; r < gridSize - 1; r += 1) {
      if (grid[r][c] === grid[r + 1][c]) {
        return true;
      }
    }
  }
  return false;
}

function handleMove(direction) {
  if (overlayEl.hidden === false) {
    return;
  }

  if (direction === "left") {
    const { newGrid, moved, gained } = moveLeft();
    if (!moved) {
      return;
    }
    grid = newGrid;
    score += gained;
    addTile();
    render();
  } else {
    const rotated = rotateGrid(direction);
    const original = grid;
    grid = rotated;
    const { newGrid, moved, gained } = moveLeft();
    if (!moved) {
      grid = original;
      return;
    }
    score += gained;
    setGrid(newGrid, direction);
    addTile();
    render();
  }

  if (!canMove()) {
    overlayEl.hidden = false;
  }
}

function handleKey(event) {
  const key = (event.key || "").toLowerCase();
  const code = (event.code || "").toLowerCase();
  if (["arrowup", "w", "keyw"].includes(key) || ["arrowup", "keyw"].includes(code)) {
    event.preventDefault();
    handleMove("up");
  } else if (["arrowdown", "s", "keys"].includes(key) || ["arrowdown", "keys"].includes(code)) {
    event.preventDefault();
    handleMove("down");
  } else if (["arrowleft", "a", "keya"].includes(key) || ["arrowleft", "keya"].includes(code)) {
    event.preventDefault();
    handleMove("left");
  } else if (["arrowright", "d", "keyd"].includes(key) || ["arrowright", "keyd"].includes(code)) {
    event.preventDefault();
    handleMove("right");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initGame();
  window.addEventListener("keydown", handleKey);
  restartBtn.addEventListener("click", initGame);
  playAgainBtn.addEventListener("click", initGame);
});
