import React, { useEffect, useState, useRef } from "react";
import { Dashboard } from "./components/Dashboard";
import Header from "./components/Header";
import Dropdown from "./components/Dropdown";
import MapComponent from "./components/Map";
import Form from "./components/Form";
import "./main.css";
import { DashboardWithBar } from "./components/DashboardWithBar";
import PeriodFilter from "./components/PeriodFilter";
import { toPng } from "html-to-image";
import download from "downloadjs";

function App() {
  const [page, setPage] = useState("main");

  const [uavTypes, setUavTypes] = useState<{ value: string; label: string }[]>([]);
  const [selectedUav, setSelectedUav] = useState<string | null>(null);

  const [regions, setRegions] = useState<{ value: string; label: string }[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [stats, setStats] = useState<{ totalPeriod: number; totalYear: number }>({
    totalPeriod: 0,
    totalYear: 0,
  });

  // ref на скрытый input
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    const file = e.target.files[0];

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://backend:8000/flights/import-xlsx", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Ошибка при импорте файла");

      const result = await response.json();
      alert(`Импортировано записей: ${result.imported}`);
    } catch (err) {
      console.error(err);
      alert("Ошибка при отправке файла");
    } finally {
      e.target.value = ""; // очищаем input, чтобы можно было выбрать тот же файл
    }
  };

  const handleDownload = async () => {
    const dashboard = document.querySelector(".AppContent")?.parentElement as HTMLElement;
    if (!dashboard) return alert("Дашборд не найден!");

    try {
      const dataUrl = await toPng(dashboard, {
        backgroundColor: "white",
        cacheBust: true,
      });
      download(dataUrl, "dashboard.png", "image/png");
    } catch (err) {
      console.error("Ошибка при сохранении дашборда:", err);
    }
  };

  useEffect(() => {
    fetch("http://backend:8000/flights/types")
      .then((res) => res.json())
      .then((data) =>
        setUavTypes(data.map((f: any) => ({ value: f.uav_type, label: f.uav_type })))
      )
      .catch((err) => console.error("Ошибка загрузки типов БПЛА:", err));
  }, []);

  useEffect(() => {
    fetch("http://backend:8000/flights/cities")
      .then((res) => res.json())
      .then((data) =>
        setRegions(data.map((f: any) => ({ value: f.city, label: f.city })))
      )
      .catch((err) => console.error("Ошибка загрузки городов:", err));
  }, []);

  const fetchStats = () => {
    let url = "http://backend:8000/flights/stats?";
    const params = new URLSearchParams();

    if (selectedUav) params.append("uav_type", selectedUav);
    if (selectedRegion) params.append("city", selectedRegion);
    if (startDate) params.append("startDate", startDate);
    if (endDate) params.append("endDate", endDate);

    url += params.toString();

    fetch(url)
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Ошибка загрузки статистики:", err));
  };

  useEffect(() => {
    fetchStats();
  }, [selectedUav, selectedRegion, startDate, endDate]);

  return (
    <div className="AppContent">
      <Header page={page} setPage={setPage} />
      {page === "main" ? (
        <div>
          <div className="twoColumns">
            <div className="leftColumn">
              <div className="Choise">
                <Dropdown
                  label="Тип БПЛА"
                  options={uavTypes}
                  value={selectedUav || ""}
                  onChange={(val) => setSelectedUav(val as string)}
                />
                <Dropdown
                  label="Регион"
                  options={regions}
                  value={selectedRegion || ""}
                  onChange={(val) => setSelectedRegion(val as string)}
                />
                <PeriodFilter
                  startDate={startDate}
                  endDate={endDate}
                  onChange={(start, end) => {
                    setStartDate(start);
                    setEndDate(end);
                  }}
                />
              </div>

              <div className="statsContainer">
                <div className="statBlock">
                  <p className="textBlue">
                    Количество полетов «{selectedUav || "БПЛА"}» в «{selectedRegion || "регионе"}» за выбранный период
                  </p>
                  <p className="statsText">{stats.totalPeriod}</p>
                </div>
                <div className="divider"></div>
                <div className="statBlock1">
                  <p className="textBlue">Количество полетов за год по РФ</p>
                  <p className="statsText">{stats.totalYear}</p>
                </div>
              </div>

              <div className="DashBoardWithBar">
                <DashboardWithBar
                  filters={{
                    startDate: startDate || undefined,
                    endDate: endDate || undefined,
                  }}
                />
              </div>
            </div>

            <div className="rightColumn">
              <div className="Buttons">
                {/* кнопка Импорт */}
                <button className="download-btn" onClick={handleImportClick}>
                  Импорт данных
                </button>
                {/* скрытый input */}
                <input
                  type="file"
                  accept=".xlsx"
                  ref={fileInputRef}
                  style={{ display: "none" }}
                  onChange={handleFileSelect}
                />
                <button className="download-btn" onClick={handleDownload}>
                  Экспорт данных
                </button>
              </div>

              <div className="flightInfoBlock">
                <div className="infoCard"> 
                  <p className="label">Состояние</p>
                   <p className="value">В полете</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Координаты начала</p> 
                  <p className="value">5503N08250E</p>
                </div>
                <div className="infoCard"> 
                  <p className="label">Координаты конца</p>
                  <p className="value">5503N08250E</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Маршрут</p> 
                  <p className="value">?????</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Тип БПЛА</p> 
                  <p className="value">1BPLA</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Регистрационный №</p> 
                  <p className="value">0944N80</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Время начала</p> 
                  <p className="value">16:32:00</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Время конца</p> 
                  <p className="value">17:34:00</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Общая длительность</p> 
                  <p className="value">01:02:00</p> 
                </div> 
                <div className="infoCard"> 
                  <p className="label">Максимальная высота</p> 
                  <p className="value">1200 м</p> 
                </div>
              </div>

              <div className="MapPlace">
                <MapComponent />
              </div>
            </div>
          </div>

          <div className="DashBoard">
            <Dashboard
              filters={{
                city: selectedRegion || undefined,
                uav_type: selectedUav || undefined,
              }}
            />
          </div>
          <div className="space"></div>
        </div>
      ) : page === "form" ? (
        <Form />
      ) : null}
    </div>
  );
}

export default App;
