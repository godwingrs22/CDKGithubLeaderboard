import React from 'react';
import logo from '../assets/cdk_logo.png';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <img src={logo} alt="Logo" className="logo" />
        <h1 className="header-title">AWS CDK</h1>
      </div>
    </header>
  );
}

export default Header;
