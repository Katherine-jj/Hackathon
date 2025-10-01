import React, { useState, useRef, useEffect } from "react";
import { DateRange } from "react-date-range";
import "react-date-range/dist/styles.css";
import "react-date-range/dist/theme/default.css";

type Props = {
  startDate: string;
  endDate: string;
  onChange: (start: string, end: string) => void;
};

function PeriodFilter({ startDate, endDate, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const formatted =
    startDate && endDate
      ? `${startDate} — ${endDate}`
      : "Не выбрано";

  return (
    <div className="dropdown-wrapper" ref={ref}>
      <label className="dropdown-label">Период</label>
      <button
        className="dropdown"
        style={{ textAlign: "left" }}
        onClick={() => setOpen((prev) => !prev)}
      >
        {formatted}
      </button>

      {open && (
        <div
          style={{
            position: "absolute",
            zIndex: 1100, 
            background: "white",
            border: "1px solid #ddd",
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            marginTop: "8px",
          }}
        >
          <DateRange
            editableDateInputs={true}
            moveRangeOnFirstSelection={false}
            ranges={[
              {
                startDate: startDate ? new Date(startDate) : new Date(),
                endDate: endDate ? new Date(endDate) : new Date(),
                key: "selection",
              },
            ]}
            onChange={(ranges) => {
              const { startDate, endDate } = ranges.selection;
              onChange(
                startDate?.toISOString().split("T")[0] || "",
                endDate?.toISOString().split("T")[0] || ""
              );
            }}
          />
        </div>
      )}
    </div>
  );
}

export default PeriodFilter;
