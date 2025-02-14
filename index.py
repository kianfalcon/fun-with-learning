import React, { useState } from 'react';

// Icon components
const SmallIcon = ({ children }) => (
  <span className="text-base">{children}</span>
);

const GameIcon = ({ children }) => (
  <span className="text-2xl">{children}</span>
);

const BinaryPuzzleGame = () => {
  const puzzleConfigurations = [
    [
      ['recycle', null, 'chair', null],
      [null, 'chair', null, 'recycle'],
      ['chair', null, 'recycle', null],
      [null, 'recycle', null, 'chair']
    ],
    [
      ['chair', null, 'recycle', null],
      [null, 'recycle', null, 'chair'],
      ['recycle', null, 'chair', null],
      [null, 'chair', null, 'recycle']
    ],
    [
      [null, 'chair', null, 'recycle'],
      ['recycle', null, 'chair', null],
      [null, 'recycle', null, 'chair'],
      ['chair', null, 'recycle', null]
    ]
  ];

  const [currentPuzzleIndex, setCurrentPuzzleIndex] = useState(0);
  const initialGrid = puzzleConfigurations[currentPuzzleIndex];

  const handleRefresh = () => {
    const nextIndex = (currentPuzzleIndex + 1) % puzzleConfigurations.length;
    setCurrentPuzzleIndex(nextIndex);
    setGrid(puzzleConfigurations[nextIndex]);
    setHistory([puzzleConfigurations[nextIndex]]);
    setCurrentStep(0);
    setErrors([]);
    setErrorCells(new Set());
    setHintCell(null);
    setSeconds(0);
    setIsActive(true);
  };

  const [grid, setGrid] = useState(initialGrid);
  const [history, setHistory] = useState([initialGrid]);
  const [currentStep, setCurrentStep] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [errors, setErrors] = useState([]);
  const [errorCells, setErrorCells] = useState(new Set());
  const [hintCell, setHintCell] = useState(null);
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(true);

  // Timer effect
  React.useEffect(() => {
    let interval = null;
    if (isActive) {
      interval = setInterval(() => {
        setSeconds(seconds => seconds + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isActive]);

  // Format time for display
  const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
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
    setSeconds(0); // Reset timer
    setIsActive(true); // Start timer again
  };

  const validateCell = (grid, row, col) => {
    const errorCells = new Set();
    const errors = new Map();
    
    // Check current row
    const currentRow = grid[row];
    const chairs = currentRow.filter(cell => cell === 'chair').length;
    const recycles = currentRow.filter(cell => cell === 'recycle').length;
    
    // Check three consecutive in row
    for (let j = 0; j < 2; j++) {
      if (grid[row][j] && grid[row][j] === grid[row][j+1] && grid[row][j] === grid[row][j+2]) {
        errors.set('consecutive', {
          message: `No more than 2 same symbols may be next to each other`,
          type: 'count'
        });
        // Highlight full row
        for (let k = 0; k < 4; k++) {
          errorCells.add(`${row}-${k}`);
        }
      }
    }

    // Check three consecutive in column
    for (let i = 0; i < 2; i++) {
      if (grid[i][col] && grid[i][col] === grid[i+1][col] && grid[i][col] === grid[i+2][col]) {
        errors.set('consecutive', {
          message: `No more than 2 same symbols may be next to each other`,
          type: 'count'
        });
        // Highlight full column
        for (let k = 0; k < 4; k++) {
          errorCells.add(`${k}-${col}`);
        }
      }
    }

    // Check row balance
    if (chairs !== recycles && chairs + recycles === 4) {
      errors.set('balance', {
        message: `Each row and column must contain equal number of symbols`,
        type: 'balance'
      });
      // Highlight full row
      for (let i = 0; i < 4; i++) {
        errorCells.add(`${row}-${i}`);
      }
    }

    // Check column balance
    const currentCol = grid.map(r => r[col]);
    const colChairs = currentCol.filter(cell => cell === 'chair').length;
    const colRecycles = currentCol.filter(cell => cell === 'recycle').length;
    if (colChairs !== colRecycles && colChairs + colRecycles === 4) {
      errors.set('balance', {
        message: `Each row and column must contain equal number of symbols`,
        type: 'balance'
      });
      // Highlight full column
      for (let i = 0; i < 4; i++) {
        errorCells.add(`${i}-${col}`);
      }
    }

    // Check = patterns
    const equalPatterns = [[[0,0], [0,1]], [[0,0], [1,0]]];
    equalPatterns.forEach(([[r1, c1], [r2, c2]]) => {
      if ((row === r1 && col === c1) || (row === r2 && col === c2)) {
        const cell1 = grid[r1][c1];
        const cell2 = grid[r2][c2];
        if (cell1 && cell2 && cell1 !== cell2) {
          errors.set('equal-pattern', {
            message: `Cells connected by = must be the same`,
            type: 'equal-pattern'
          });
          errorCells.add(`${r1}-${c1}`);
          errorCells.add(`${r2}-${c2}`);
        }
      }
    });

    return { errors: [...errors.values()], errorCells };
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
    
    // Delay error checking by 800ms
    setTimeout(() => {
      const { errors: newErrors, errorCells: newErrorCells } = validateCell(newGrid, row, col);
      setErrors(newErrors);
      setErrorCells(newErrorCells);
    }, 800);
    
    // Check for victory condition
    if (isGameComplete(newGrid)) {
      setIsActive(false); // Stop timer
    }
    
    // Update history
    const newHistory = history.slice(0, currentStep + 1);
    newHistory.push(JSON.parse(JSON.stringify(newGrid)));
    setHistory(newHistory);
    setCurrentStep(currentStep + 1);
  };

  const handleUndo = () => {
    if (currentStep > 0) {
      const previousStep = currentStep - 1;
      setCurrentStep(previousStep);
      const previousGrid = JSON.parse(JSON.stringify(history[previousStep]));
      setGrid(previousGrid);
      
      // Only check for consecutive and balance errors when undoing
      const { errors: newErrors, errorCells: newErrorCells } = validateCell(previousGrid);
      const filteredErrors = newErrors.filter(error => 
        error.type === 'consecutive' || error.type === 'balance'
      );
      
      const filteredErrorCells = new Set();
      filteredErrors.forEach(error => {
        error.cells.forEach(cell => filteredErrorCells.add(cell));
      });
      
      setErrors(filteredErrors);
      setErrorCells(filteredErrorCells);
    }
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
            onClick={handleRefresh}
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
        {/* Grid Cells */}
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

      {/* Victory Message */}
      {isGameComplete(grid) && (
        <div className="bg-green-50 border-2 border-green-300 p-4 rounded-lg shadow-lg w-[264px]">
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

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="flex flex-col gap-1 w-[264px]">
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
        <div className="text-sm bg-yellow-50 border-2 border-yellow-200 p-3 rounded-lg w-[264px]">
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
    </div>
  );
};

export default BinaryPuzzleGame;
