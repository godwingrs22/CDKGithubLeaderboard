import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import TopThree from "./components/TopThree";
import LeaderboardTable from "./components/LeaderboardTable";
import InfoBoards from './components/InfoBoards';
import "./styles/App.css";

function App() {
  const [leaderboardData, setLeaderboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For local development
    // fetch("/test/leaderboard.json")
      fetch('/data/leaderboard.json')
      .then((response) => response.json())
      .then((data) => {
        // Sort the data by total score in descending order
        const sortedData = [...data.contributors].sort(
          (a, b) => b.totalScore - a.totalScore
        );
        setLeaderboardData({
          ...data,
          contributors: sortedData,
        });
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  const sortedData = [...(leaderboardData?.contributors || [])].sort(
    (a, b) => b.totalScore - a.totalScore
  );

  return (
    <div className="App">
      <Header />
      <h1 className="main-title">
        <img src={require('./assets/champion_icon.png')} alt="champion" className="champion-icon" />
        Top 100 Contributors Leaderboard
        <img src={require('./assets/champion_icon.png')} alt="champion" className="champion-icon" />
      </h1>
      <TopThree winners={sortedData.slice(0, 3)} />
      <InfoBoards />
      <LeaderboardTable data={sortedData} />
      <div className="footer-info">
        <div className="last-updated">
          Last Updated:{" "}
          {new Date(leaderboardData?.lastUpdated).toLocaleString()}
        </div>
        <div className="data-note">* Based on data since January 1, 2024</div>
      </div>
    </div>
  );
}

export default App;
