import React, { useState } from "react";
import "./App.css";
import BilliardHallSVG from "./BilliardHallSVG.jsx";

// MOCK DATA
const tables = [
  { id: 1, name: "Стол 1", busy: false },
  { id: 2, name: "Стол 2", busy: true },
  { id: 3, name: "Стол 3", busy: false },
  { id: 4, name: "Стол 4", busy: false },
];

function TableScheme({ tables, selectedTable, onSelect }) {
  // (оставим для будущей интерактивности, пока скрыто)
  return null;
}

function DatePicker({ selectedDate, onSelect }) {
  // MOCK: next 5 days, today is active, past is disabled
  const today = new Date();
  const days = Array.from({ length: 5 }, (_, i) => {
    const d = new Date();
    d.setDate(today.getDate() + i);
    return d;
  });
  return (
    <div className="booking-block">
      <div className="block-title">Дата</div>
      <div className="date-picker no-scroll">
        {days.map((d) => {
          const isPast = d < today;
          const isSelected = selectedDate && d.toDateString() === selectedDate.toDateString();
          return (
            <button
              key={d.toISOString()}
              className={`date-btn${isPast ? " past" : ""}${isSelected ? " selected" : ""}`}
              disabled={isPast}
              onClick={() => onSelect(new Date(d))}
            >
              {d.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" })}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function TimeSlots({ slots, selectedSlots, onSelect }) {
  // Разбиваем слоты на ряды по 4
  const chunkSize = 4;
  const rows = [];
  for (let i = 0; i < slots.length; i += chunkSize) {
    rows.push(slots.slice(i, i + chunkSize));
  }
  return (
    <div className="booking-block">
      <div className="block-title">Время</div>
      <div className="timeslots-picker-grid">
        {rows.map((row, idx) => (
          <div className="timeslot-row" key={idx}>
            {row.map((slot) => (
              <button
                key={slot.time}
                className={`slot-btn${slot.busy ? " busy" : ""}${selectedSlots.includes(slot.time) ? " selected" : ""}`}
                disabled={slot.busy}
                onClick={() => onSelect(slot.time)}
              >
                {slot.time}
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function BookingPage({ onSubmit, onCancel }) {
  const [selectedTable, setSelectedTable] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedSlots, setSelectedSlots] = useState([]);

  // MOCK: генерируем интервалы (15:00-16:00 и т.д.)
  const slots = Array.from({ length: 8 }, (_, i) => {
    const start = 15 + i;
    const end = start + 1;
    return {
      time: `${start}:00-${end}:00`,
      busy: i === 2 || i === 4,
    };
  });

  // MOCK: занятые столы (например, 2 и 5)
  const busyTables = [2, 5];

  function handleSlotClick(time) {
    setSelectedSlots((prev) =>
      prev.includes(time)
        ? prev.filter((t) => t !== time)
        : [...prev, time]
    );
  }

  function handleSubmit() {
    if (selectedTable && selectedDate && selectedSlots.length) {
      onSubmit({ table: selectedTable, date: selectedDate, slots: selectedSlots });
    }
  }

  return (
    <div className="booking-page">
      <BilliardHallSVG
        selectedTable={selectedTable}
        busyTables={busyTables}
        onSelect={setSelectedTable}
        className="billiard-hall-svg"
        style={{ marginBottom: 24 }}
      />
      <DatePicker selectedDate={selectedDate} onSelect={setSelectedDate} />
      <TimeSlots slots={slots} selectedSlots={selectedSlots} onSelect={handleSlotClick} />
      <button
        className="neumorphic-button primary"
        style={{ marginTop: 32 }}
        disabled={!(selectedTable && selectedDate && selectedSlots.length)}
        onClick={handleSubmit}
      >
        Забронировать
      </button>
      <button
        className="neumorphic-button"
        style={{ marginTop: 12, fontSize: 14 }}
        onClick={onCancel}
      >
        Отмена
      </button>
    </div>
  );
}
