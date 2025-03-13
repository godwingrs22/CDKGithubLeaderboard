import React from 'react';

function SearchBar({ onSearch }) {
  return (
    <div className="search-container">
      <input
        type="text"
        placeholder="Search username"
        onChange={(e) => onSearch(e.target.value)}
        className="search-input"
      />
      <svg 
        className="search-icon" 
        xmlns="http://www.w3.org/2000/svg" 
        width="20" 
        height="20" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      >
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
    </div>
  );
}

export default SearchBar;
