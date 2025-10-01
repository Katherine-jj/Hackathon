interface DropdownProps {
  label: string;
  options: { value: string | number; label: string }[];
  value: string | number | null;
  onChange: (value: string | number) => void;
}

function Dropdown({ label, options, value, onChange }: DropdownProps) {
  return (
    <div className="dropdown-wrapper">
      <label className="dropdown-label">{label}</label>
      <select
        className="dropdown"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Не выбрано</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export default Dropdown;
