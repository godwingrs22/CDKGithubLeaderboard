import React from 'react';

function Footer({ lastUpdated }) {
  return (
    <footer className="footer-info">
      <div className="last-updated">
        Last Updated: {new Date(lastUpdated).toLocaleString()}
      </div>
      <div className="data-note">
        * Based on data since January 1, 2024
      </div>
    </footer>
  );
}

export default Footer;
