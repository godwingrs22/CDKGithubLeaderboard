import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import Footer from './components/Footer'; 
import TopThree from "./components/TopThree";
import LeaderboardTable from "./components/LeaderboardTable";
import InfoBoards from './components/InfoBoards';
import "./styles/App.css";

function sortContributors(contributors) {
  return [...contributors].sort((a, b) => {
    if(a.totalScore === b.totalScore) {
      if(a.prsMerged !== b.prsMerged) {
        return b.prsMerged - a.prsMerged;
      }
      else if(a.prsReviewed !== b.prsReviewed) {
        return b.prsReviewed - a.prsReviewed;
      }
      else if(a.issuesOpened !== b.issuesOpened){
        return b.issuesOpened - a.issuesOpened;
      }
      else if(a.discussionsAnswered !== b.discussionsAnswered){
        return b.discussionsAnswered - a.discussionsAnswered;
      }
    }
    return b.totalScore - a.totalScore;
  });
}

function App() {
  const [leaderboardData, setLeaderboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For local development
    // fetch('/test/leaderboard.json')
    fetch('/data/leaderboard.json')
      .then(response => response.json())
      .then(data => {
        setLeaderboardData({
          ...data,
          contributors: sortContributors(data.contributors),
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

  const sortedData = sortContributors(leaderboardData?.contributors || []);

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
      <Footer lastUpdated={leaderboardData?.lastUpdated} />
    </div>
  );
}

export default App;
