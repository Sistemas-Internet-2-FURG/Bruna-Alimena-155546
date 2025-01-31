import React from "react";
import { Link } from "react-router-dom";

const Header = ({ onLogout }) => {
  const handleLogout = () => {
    onLogout();
  };

  return (
    <header>
      <h1>My App</h1>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/register">Register</Link>
        <button onClick={handleLogout}>Logout</button>
      </nav>
    </header>
  );
};

export default Header;
