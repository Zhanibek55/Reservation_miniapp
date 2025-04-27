import React from "react";

/**
 * Интерактивная SVG-схема зала для React.
 * Для интерактивности: на каждый стол навешивается onClick, цвет подсвечивается по selected/busy.
 * Пропсы:
 *   selectedTable (номер), busyTables (массив номеров), onSelect (функция)
 */
export default function BilliardHallSVG({ selectedTable, busyTables = [], onSelect, className, style }) {
  // Массив столов с координатами и размерами
  const tables = [
    { id: 1, x: 230, y: 50, w: 160, h: 80 },
    { id: 2, x: 430, y: 50, w: 160, h: 80 },
    { id: 3, x: 630, y: 50, w: 160, h: 80 },
    { id: 4, x: 330, y: 200, w: 160, h: 80 },
    { id: 5, x: 530, y: 200, w: 160, h: 80 },
    { id: 6, x: 330, y: 350, w: 160, h: 80 },
    { id: 7, x: 530, y: 350, w: 160, h: 80 },
    { id: 8, x: 80,  y: 400, w: 80,  h: 160 },
    { id: 9, x: 80,  y: 100, w: 80,  h: 160 },
  ];
  return (
    <div className={className} style={style}>
      <svg viewBox="0 0 800 600" width="100%" height="100%" style={{ background: "#23242a", borderRadius: 16, width: "100%", height: "auto" }}>
        {/* Стены */}
        <line x1="200" y1="0" x2="200" y2="600" stroke="black" strokeWidth={4} />
        <line x1="0" y1="300" x2="200" y2="300" stroke="black" strokeWidth={4} />
        {/* Столы */}
        {tables.map((tbl) => {
          const isBusy = busyTables.includes(tbl.id);
          const isSelected = selectedTable === tbl.id;
          return (
            <g key={tbl.id} style={{ cursor: isBusy ? "not-allowed" : "pointer" }} onClick={() => !isBusy && onSelect && onSelect(tbl.id)}>
              <rect
                x={tbl.x}
                y={tbl.y}
                width={tbl.w}
                height={tbl.h}
                fill={isBusy ? "#c62828" : isSelected ? "#4fc3f7" : "#43a047"}
                stroke={isSelected ? "#1976d2" : "black"}
                strokeWidth={isSelected ? 6 : 3}
                opacity={isBusy ? 0.7 : 1}
                rx={14}
                ry={14}
              />
              <text
                x={tbl.x + tbl.w / 2}
                y={tbl.y + tbl.h / 2 + 8}
                fontSize={36}
                fill={isSelected ? "#222" : "#fff"}
                fontWeight="bold"
                textAnchor="middle"
                pointerEvents="none"
              >
                {tbl.id}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
