import React, { useState } from 'react';

const SmallIcon = ({ children }) => (
  <span className="text-base">{children}</span>
);

const GameIcon = ({ children }) => (
  <span className="text-2xl">{children}</span>
);

const BinaryPuzzleGame = () => {
  const initialGrid = [
    ['chair', null, 'recycle', null],
    [null, 'recycle', null, 'chair'],
    ['chair', null, 'recycle', null],
    [null, 'recycle', null, 'chair']
  ];

  const [grid, setGrid] = useState(initialGrid);
  const [history, setHistory] = useState([initialGrid]);
  const [currentStep, setCurrentStep] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [errors, setErrors] = useState([]);
  const [errorCells, setErrorCells] = useState(new Set());
  const [hintCell, setHintCell] = useState(null);
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(true);

  React.useEffect(() => {
    let interval = null;
    if (isActive) {
      interval = setInterval(() => {
        setSeconds(seconds => seconds + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isActive]);

  const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const validateCell = (grid) => {
    const errorCells = new Set();
    const errors = new Map();
    
    // Check three consecutive horizontally
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j <= 1; j++) {
        if (grid[i][j] && grid[i][j+1] && grid[i][j+2] &&
            grid[i][j] === grid[i][j+1] && grid[i][j] === grid[i][j+2]) {
          errors.set(`consecutive-row-${i}-${j}`, {
            message: `Row ${i+1} has three consecutive ${grid[i][j] === 'chair' ? 'chairs' : 'leaves'}`,
            type: 'consecutive',
            cells: [`${i}-${j}`, `${i}-${j+1}`, `${i}-${j+2}`]
          });
          for (let k = 0; k < 4; k++) {
            errorCells.add(`${i}-${k}`);
          }
        }
      }
    }

    // Check three consecutive vertically
    for (let j = 0; j < 4; j++) {
      for (let i = 0; i <= 1; i++) {
        if (grid[i][j] && grid[i+1][j] && grid[i+2][j] &&
            grid[i][j] === grid[i+1][j] && grid[i][j] === grid[i+2][j]) {
          errors.set(`consecutive-col-${j}-${i}`, {
            message: `Column ${j+1} has three consecutive ${grid[i][j] === 'chair' ? 'chairs' : 'leaves'}`,
            type: 'consecutive',
            cells: [`${i}-${j}`, `${i+1}-${j}`, `${i+2}-${j}`]
          });
          for (let k = 0; k < 4; k++) {
            errorCells.add(`${k}-${j}`);
          }
        }
      }
    }

    // Row balance check
    for (let i = 0; i < 4; i++) {
      const rowCells = grid[i].filter(cell => cell !== null);
      if (rowCells.length === 4) {
        const chairs = rowCells.filter(cell => cell === 'chair').length;
        const recycles = rowCells.filter(cell => cell === 'recycle').length;
        if (chairs !== 2 || recycles !== 2) {
          errors.set(`balance-row-${i}`, {
            message: `Row ${i+1} must have 2 chairs and 2 leaves`,
            type: 'balance',
            cells: Array.from({length: 4}, (_, j) => `${i}-${j}`)
          });
          for (let j = 0; j < 4; j++) {
            errorCells.add(`${i}-${j}`);
          }
        }
      }
    }

    // Column balance check
    for (let j = 0; j < 4; j++) {
      const colCells = grid.map(row => row[j]).filter(cell => cell !== null);
      if (colCells.length === 4) {
        const chairs = colCells.filter(cell => cell === 'chair').length;
        const recycles = colCells.filter(cell => cell === 'recycle').length;
        if (chairs !== 2 || recycles !== 2) {
          errors.set(`balance-col-${j}`, {
            message: `Column ${j+1} must have 2 chairs and 2 leaves`,
            type: 'balance',
            cells: Array.from({length: 4}, (_, i) => `${i}-${j}`)
          });
          for (let i = 0; i < 4; i++) {
            errorCells.add(`${i}-${j}`);
          }
        }
      }
    }

    return { errors: [...errors.values()], errorCells };
  };

  const handleCellClick = (row, col) => {
    const isInitialCell = initialGrid[row][col] !== null;
    if (isInitialCell) return;

    const newGrid = grid.map(r => [...r]);
    
    if (!newGrid[row][col]) {
      newGrid[row][col] = 'chair';
    } else if (newGrid[row][col] === 'chair') {
      newGrid[row][col] = 'recycle';
    } else {
      newGrid[row][col] = null;
    }

    setGrid(newGrid);
    
    // Only maintain error cells from consecutive and balance rules
    const { errors: newErrors, errorCells: newErrorCells } = validateCell(newGrid);
    
    setErrors(newErrors);
    setErrorCells(newErrorCells);
    
    // Update history
    const newHistory = history.slice(0, currentStep + 1);
    newHistory.push(JSON.parse(JSON.stringify(newGrid)));
    setHistory(newHistory);
    setCurrentStep(currentStep + 1);

    // Check for completion
    if (isGameComplete(newGrid)) {
      setIsActive(false);
    }
  };

  const handleUndo = () => {
    if (currentStep > 0) {
      const previousStep = currentStep - 1;
      setCurrentStep(previousStep);
      const previousGrid = JSON.parse(JSON.stringify(history[previousStep]));
      setGrid(previousGrid);
      
      // Only check for consecutive and balance errors when undoing
      const { errors: newErrors, errorCells: newErrorCells } = validateCell(previousGrid);
      setErrors(newErrors);
      setErrorCells(newErrorCells);
    }
  };

  const handleClear = () => {
    const clearedGrid = initialGrid.map(row => 
      row.map(cell => cell === null ? null : cell)
    );
    setGrid(clearedGrid);
    setHistory([clearedGrid]);
    setCurrentStep(0);
    setErrors([]);
    setErrorCells(new Set());
    setHintCell(null);
    setSeconds(0);
    setIsActive(true);
  };

  const getHint = () => {
    if (isGameComplete(grid)) {
      setShowHint(true);
      setTimeout(() => {
        setShowHint(false);
      }, 3000);
      return;
    }

    // Only check for consecutive and balance errors
    if (errors.length > 0) {
      const validErrors = errors.filter(error => 
        error.type === 'consecutive' || error.type === 'balance'
      );
      
      if (validErrors.length > 0 && validErrors[0].cells) {
        for (const cell of validErrors[0].cells) {
          const [row, col] = cell.split('-').map(Number);
          if (initialGrid[row][col] === null && grid[row][col] !== null) {
            setHintCell(cell);
            setShowHint(true);
            setTimeout(() => {
              setShowHint(false);
              setHintCell(null);
            }, 3000);
            return;
          }
        }
      }
    }
    
    setShowHint(true);
    setTimeout(() => {
      setShowHint(false);
      setHintCell(null);
    }, 3000);
  };

  const isGameComplete = (grid) => {
    // Check if all cells are filled
    const isFilled = grid.every(row => row.every(cell => cell !== null));
    if (!isFilled) return false;

    // Check rows and columns for balance (2 of each symbol)
    for (let i = 0; i < 4; i++) {
      const row = grid[i];
      const col = grid.map(r => r[i]);
      
      const rowChairs = row.filter(cell => cell === 'chair').length;
      const rowRecycles = row.filter(cell => cell === 'recycle').length;
      const colChairs = col.filter(cell => cell === 'chair').length;
      const colRecycles = col.filter(cell => cell === 'recycle').length;
      
      if (rowChairs !== 2 || rowRecycles !== 2 || colChairs !== 2 || colRecycles !== 2) return false;
    }

    // Check for three consecutive symbols
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 2; j++) {
        // Check horizontal
        if (grid[i][j] === grid[i][j+1] && grid[i][j] === grid[i][j+2]) return false;
        // Check vertical
        if (grid[j][i] === grid[j+1][i] && grid[j][i] === grid[j+2][i]) return false;
      }
    }

    return true;
  };

  return (
    <div className="flex flex-col items-center gap-6 p-6 max-w-md mx-auto bg-white rounded-xl shadow-lg">
      {/* Title, Subtitle, Timer and Refresh */}
      <div className="text-center">
        <h1 className="text-2xl font-bold">
          <span className="text-black">KIAN</span>{' '}
          <span className="text-red-600">Falcon</span>
        </h1>
        <p className="text-sm text-black mt-1">Furniture made fun, accessible, and sustainable</p>
        <div className="flex items-center justify-center gap-2 mt-2">
          <div className="text-lg font-mono">{formatTime(seconds)}</div>
          <button
            onClick={handleClear}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
            title="New Puzzle"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Game grid */}
      <div className="grid grid-cols-4 gap-px bg-gray-300 p-px rounded-lg">
        {grid.map((row, rowIndex) => (
          row.map((cell, colIndex) => {
            const isInitialCell = initialGrid[rowIndex][colIndex] !== null;
            const isPuzzleComplete = isGameComplete(grid);
            return (
              <button
                key={`${rowIndex}-${colIndex}`}
                className={`
                  w-16 h-16 
                  flex items-center justify-center 
                  ${isInitialCell ? 'bg-gray-50' : 'bg-white hover:bg-gray-50'} 
                  transition-colors duration-200
                  ${errorCells.has(`${rowIndex}-${colIndex}`) ? 'bg-red-50 border-2 border-red-300' : ''}
                  ${hintCell === `${rowIndex}-${colIndex}` ? 'bg-yellow-100 border-2 border-yellow-400' : ''}
                  ${isPuzzleComplete ? 'bg-green-100 border-2 border-green-300' : ''}
                  relative z-10
                `}
                onClick={() => handleCellClick(rowIndex, colIndex)}
                disabled={isInitialCell}
              >
                {cell === 'chair' ? (
                  <GameIcon>🪑</GameIcon>
                ) : cell === 'recycle' ? (
                  <GameIcon>🌿</GameIcon>
                ) : null}
              </button>
            );
          })
        ))}
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="flex flex-col gap-1 w-64">
          {errors.filter(error => 
            error.type === 'consecutive' || error.type === 'balance'
          ).map((error, index) => (
            <div key={index} className="border border-red-300 p-2 rounded-lg bg-white text-xs text-red-600">
              {error.message}
            </div>
          ))}
        </div>
      )}

      {/* Controls */}
      <div className="flex gap-4 w-full justify-center">
        <button
          onClick={handleUndo}
          className="px-8 py-3 bg-gray-100 rounded-lg font-medium hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={currentStep === 0}
        >
          Undo
        </button>
        <button
          onClick={getHint}
          className="px-8 py-3 bg-white border-2 border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          Hint
        </button>
        <button
          onClick={handleClear}
          className="px-8 py-3 bg-gray-100 rounded-lg font-medium hover:bg-gray-200 transition-colors"
        >
          Clear
        </button>
      </div>

      {/* Hint message */}
      {showHint && (
        <div className="text-sm bg-yellow-50 border-2 border-yellow-200 p-3 rounded-lg w-64">
 <span className="font-medium">
            {isGameComplete(grid) 
              ? "All cells are correct!" 
              : hintCell 
                ? "The highlighted cell is incorrect." 
                : "Try filling in more cells."}
          </span>
        </div>
      )}

      {/* Rules */}
      <div className="w-full space-y-3 text-sm text-gray-600">
        <div className="font-semibold text-gray-700">How to play</div>
        <ul className="space-y-4">
          <li className="flex items-center gap-2">
            • Fill the grid with chairs and sustainability symbols
            <span className="flex gap-2">
              <SmallIcon>🪑</SmallIcon>
              <SmallIcon>🌿</SmallIcon>
            </span>
          </li>
          <li className="flex items-center gap-2">
            • Valid pair: 
            <div className="flex gap-1 bg-gray-100 p-1 rounded">
              <SmallIcon>🪑</SmallIcon>
              <SmallIcon>🪑</SmallIcon>
            </div>
            Invalid group:
            <div className="flex gap-1 bg-red-100 p-1 rounded">
              <SmallIcon>🪑</SmallIcon>
              <SmallIcon>🪑</SmallIcon>
              <SmallIcon>🪑</SmallIcon>
            </div>
          </li>
          <li className="flex items-center gap-2">
            • Each row and column must have equal symbols
            <div className="flex gap-1 bg-gray-100 p-1 rounded">
              <SmallIcon>🪑</SmallIcon>
              <SmallIcon>🌿</SmallIcon>
            </div>
          </li>
        </ul>
      </div>

      {/* Victory Message */}
      {isGameComplete(grid) && (
        <div className="bg-green-50 border-2 border-green-300 p-4 rounded-lg shadow-lg w-64">
          <div className="text-center">
            <h3 className="text-lg font-bold text-green-700">Congratulations! 🎉</h3>
            <p className="text-sm text-green-600 mt-2">
              You completed the puzzle in {formatTime(seconds)}!
            </p>
            <div className="mt-4 p-3 bg-green-100 rounded-lg">
              <p className="text-xs text-green-700 italic">
                "Did you know? Sustainable furniture manufacturing can reduce carbon emissions by up to 45% compared to traditional methods."
              </p>
            </div>
            <a 
              href="https://www.eagle-grp.com/kian-falcon-manufacturing-llp/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-block mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition-colors"
            >
              Learn more about KIAN Falcon
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default BinaryPuzzleGame;
