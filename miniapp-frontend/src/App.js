import React, { useEffect, useState } from "react";
import "./App.css";
import BookingPage from "./BookingPage";

const IconCalendar = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="button-icon">
    <rect x="3" y="5" width="18" height="16" rx="4" fill="currentColor" />
    <rect x="7" y="9" width="2" height="2" rx="1" fill="#1e1f25" />
    <rect x="11" y="9" width="2" height="2" rx="1" fill="#1e1f25" />
    <rect x="15" y="9" width="2" height="2" rx="1" fill="#1e1f25" />
  </svg>
);
const IconUser = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="button-icon">
    <circle cx="12" cy="9" r="4" fill="currentColor" />
    <rect x="5" y="16" width="14" height="5" rx="2.5" fill="currentColor" />
  </svg>
);
const IconList = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="button-icon">
    <rect x="5" y="7" width="14" height="2" rx="1" fill="currentColor" />
    <rect x="5" y="11" width="14" height="2" rx="1" fill="currentColor" />
    <rect x="5" y="15" width="14" height="2" rx="1" fill="currentColor" />
  </svg>
);

function App() {
  const [tgUser, setTgUser] = useState(null);
  const [authStatus, setAuthStatus] = useState(null);
  const [showBooking, setShowBooking] = useState(false);
  const [bookingResult, setBookingResult] = useState(null);

  useEffect(() => {
    console.log('window.Telegram:', window.Telegram);
    if (window.Telegram && window.Telegram.WebApp) {
      console.log('Telegram WebApp detected!');
      window.Telegram.WebApp.expand();
      const initData = window.Telegram.WebApp.initDataUnsafe;
      setTgUser(initData.user);
      // Авторизация через Telegram MiniApp
      console.log('Sending initData to /auth/telegram:', initData);
      fetch("/auth/telegram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(initData),
      })
        .then((res) => {
          console.log('Response from /auth/telegram:', res);
          return res.json().catch(e => {
            console.error('Error parsing JSON:', e);
            setAuthStatus("error-json");
            throw e;
          });
        })
        .then((data) => {
          console.log('Parsed data:', data);
          if (data && data.id && data.telegram_id) {
            setTgUser(data);
            setAuthStatus("ok");
          } else {
            setAuthStatus("error");
          }
        })
        .catch((err) => {
          console.error('Error during Telegram auth:', err);
          setAuthStatus("error");
        });
    } else {
      console.log('Telegram WebApp NOT detected!');
      setAuthStatus("not-telegram");
    }
  }, []);

  function handleBookingSubmit(data) {
    setShowBooking(false);
    setBookingResult(data);
    // TODO: отправить данные на сервер
  }

  function handleBookingCancel() {
    setShowBooking(false);
  }

  return (
    <div className="App">
      {authStatus === "ok" ? (
        <BookingPage onSubmit={handleBookingSubmit} onCancel={() => setShowBooking(false)} />
      ) : authStatus === null ? (
        <div className="loader">Авторизация через Telegram...</div>
      ) : authStatus === "not-telegram" ? (
        <div className="error">
          Откройте приложение через Telegram (мобильное приложение или <a href="https://web.telegram.org/k/" target="_blank" rel="noopener noreferrer">web.telegram.org/k</a>)
        </div>
      ) : authStatus === "error-json" ? (
        <div className="error">Ошибка разбора ответа сервера. Попробуйте позже.</div>
      ) : (
        <div className="error">Ошибка авторизации через Telegram</div>
      )}
      {bookingResult && (
        <div className="result-block">
          <div>Бронирование успешно отправлено!</div>
          <button onClick={() => setBookingResult(null)}>OK</button>
        </div>
      )}
    </div>
  );
}

export default App;
