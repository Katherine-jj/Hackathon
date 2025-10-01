import React from "react";

interface ButtonProps {
  text: string;
  onClick: () => void;
  active?: boolean;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ text, onClick, active, className }) => {
  return (
    <button
      onClick={onClick}
      className={`${className || ""} ${active ? "active" : ""}`} 
    >
      {text}
    </button>
  );
};

export default Button;
