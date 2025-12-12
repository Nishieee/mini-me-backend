import React from 'react';

interface MatrixProps {
  rows: number;
  cols: number;
  mode: 'vu' | 'static';
  levels?: number[];
  size?: number;
  gap?: number;
  palette?: {
    on: string;
    off: string;
  };
}

export const Matrix: React.FC<MatrixProps> = ({
  rows,
  cols,
  mode,
  levels = [],
  size = 12,
  gap = 2,
  palette = { on: '#FFD700', off: '#222' }
}) => {
  const getCellColor = (row: number, col: number): string => {
    if (mode === 'vu' && levels.length > 0) {
      // VU mode: use levels array to determine brightness
      const levelIndex = Math.floor((col / cols) * levels.length);
      const level = levels[levelIndex] || 0;
      
      // Map level to row (bottom row = 0, top row = rows-1)
      // Higher levels should light up more rows from bottom to top
      // Row 0 (bottom) lights up first, row 6 (top) lights up last
      const rowFromBottom = rows - 1 - row; // Invert: 0 = bottom, rows-1 = top
      const threshold = rowFromBottom / rows; // 0 to 1, where 0 is bottom
      return level > threshold ? palette.on : palette.off;
    }
    
    // Static mode or no levels
    return palette.off;
  };

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${cols}, ${size}px)`,
        gridTemplateRows: `repeat(${rows}, ${size}px)`,
        gap: `${gap}px`,
        justifyContent: 'center',
        alignItems: 'center'
      }}
    >
      {Array.from({ length: rows * cols }).map((_, index) => {
        const row = Math.floor(index / cols);
        const col = index % cols;
        return (
          <div
            key={index}
            style={{
              width: `${size}px`,
              height: `${size}px`,
              backgroundColor: getCellColor(row, col),
              borderRadius: '2px',
              transition: 'background-color 0.1s ease'
            }}
          />
        );
      })}
    </div>
  );
};

