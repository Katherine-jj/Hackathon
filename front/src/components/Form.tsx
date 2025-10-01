import React, { useState } from "react";

function Form() {
  const [formData, setFormData] = useState({
    fullName: "",
    phone: "",
    activationCode: "",
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validate = () => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.fullName)
      newErrors.fullName = "Введите ФИО (например, Иванов Иван Иванович)";

    if (!formData.phone)
      newErrors.phone = "Введите номер телефона";
    else if (!/^\+?\d{10,15}$/.test(formData.phone))
      newErrors.phone = "Введите корректный номер телефона";

    if (!formData.activationCode)
      newErrors.activationCode = "Код активации неверный";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      alert("Вход выполнен");
    }
  };

  return (
    <div className="form-wrapper">
      <form className="form-container" onSubmit={handleSubmit}>
        <h2 className="form-title">АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ</h2>

        {/* ФИО */}
        <input
          placeholder="Укажите Ваше ФИО (Формат: Иванов Иван Иванович)"
          value={formData.fullName}
          onChange={(e) =>
            setFormData({ ...formData, fullName: e.target.value })
          }
        />
        {errors.fullName && <p className="error">{errors.fullName}</p>}

        {/* Номер телефона */}
        <input
          placeholder="Укажите Ваш номер телефона (Формат: 89123456789)"
          value={formData.phone}
          onChange={(e) =>
            setFormData({ ...formData, phone: e.target.value })
          }
        />
        {errors.phone && <p className="error">{errors.phone}</p>}

        {/* Код активации */}
        <input
          type="text"
          placeholder="Введите код активации, который был отправлен"
          value={formData.activationCode}
          onChange={(e) =>
            setFormData({ ...formData, activationCode: e.target.value })
          }
        />
        {errors.activationCode && <p className="error">{errors.activationCode}</p>}

        <div className="buttonwrapper">
          <button type="submit" className="form-button">
            Войти
          </button>
        </div>
      </form>
    </div>
  );
}

export default Form;
