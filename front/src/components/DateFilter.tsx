import React, { useState } from "react";

type Props = {
  startDate: string;
  endDate: string;
  onChange: (field: "start" | "end", value: string) => void;
};

function DateFilter({ startDate, endDate, onChange }: Props) {
  return (
    <div className = "Choise">
        <div className = "dropdown-wrapper">
            <label className="dropdown-label">С даты:</label>
            <input
                className="dropdown"
                type="date"
                value={startDate}
                onChange={(e) => onChange("start", e.target.value)}
            />
        </div>

        <div className = "dropdown-wrapper">
            <label className="dropdown-label">По дату:</label>
            <input
                className="dropdown"
                type="date"
                value={endDate}
                onChange={(e) => onChange("end", e.target.value)}
            />
        </div>
    </div>
  );
}

export default DateFilter;



