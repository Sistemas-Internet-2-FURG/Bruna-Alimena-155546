import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Login from "./pages/login";
import Register from "./pages/register";
import ProductList from "./pages/productList";
import Dashboard from "./pages/dashboard";
import Header from "./services/header";
import Footer from "./services/footer";
import { api } from "./services/api";

const App = () => {
  const [token, setToken] = useState(localStorage.getItem("token"));

  const handleLogin = async (username, password) => {
    try {
      console.log("enviou aqui")
      const response = await api.post("api/login", { username, password }); // Enviando via POST
      console.log("Resposta do backend:", response.data);
    } catch (error) {
      console.error("Erro ao fazer login:", error.response?.data || error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <Router>
      <Header onLogout={handleLogout} />
      <div className="container">
        <Routes>
          <Route path="/" element={token ? <ProductList /> : <Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
      <Footer />
    </Router>
  );
};

export default App;
