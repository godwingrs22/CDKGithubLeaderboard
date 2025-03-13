import React, { useMemo } from "react";
import Pagination from "./Pagination";
import RankBadge from "./RankBadge";
import SearchBar from "./SearchBar";
import defaultAvatar from "../assets/sample_user.png";

function LeaderboardTable({ data }) {
  const [currentPage, setCurrentPage] = React.useState(1);
  const [searchTerm, setSearchTerm] = React.useState("");
  const itemsPerPage = 20;

  const filteredData = useMemo(() => {
    return data.filter((contributor) =>
      contributor.username.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [data, searchTerm]);

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentData = filteredData.slice(startIndex, endIndex);

  const getGithubAvatar = (username) => `https://github.com/${username}.png`;

  const handleSearch = (value) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    document.querySelector(".table-container").scrollIntoView({
      behavior: "smooth",
    });
  };

  // Function to get original rank of a contributor
  const getOriginalRank = (username) => {
    return data.findIndex(contributor => contributor.username === username) + 1;
  };

  return (
    <div className="leaderboard-section">
      <div className="table-header">
        <h2 className="table-title">Contributors Ranking</h2>
        <SearchBar onSearch={handleSearch} />
      </div>
      {currentData.length === 0 ? (
        <div className="no-results">
          No contributors found matching "{searchTerm}"
        </div>
      ) : (
        <div className="table-container">
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th></th>
                <th>RANK</th>
                <th>USER NAME</th>
                <th>PRS MERGED</th>
                <th>PRS REVIEWED</th>
                <th>ISSUES CREATED</th>
                <th>DISCUSSIONS ANSWERED</th>
                <th>TOTAL SCORE</th>
              </tr>
            </thead>
            <tbody>
              {currentData.map((contributor, index) => {
                const originalRank = getOriginalRank(contributor.username);
                return (
                  <tr key={contributor.username}>
                    <td className="badge-cell">
                      <RankBadge rank={originalRank} />
                    </td>
                    <td className="rank-cell">{originalRank}</td>
                    <td>
                      <div className="user-cell">
                        <img
                          src={getGithubAvatar(contributor.username)}
                          alt="avatar"
                          className="avatar"
                          onError={(e) => (e.target.src = defaultAvatar)}
                        />
                        <span>{contributor.username}</span>
                      </div>
                    </td>
                    <td>{contributor.prsMerged}</td>
                    <td>{contributor.prsReviewed}</td>
                    <td>{contributor.issuesCreated}</td>
                    <td>{contributor.discussionsAnswered}</td>
                    <td className="total-score">{contributor.totalScore}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
}

export default LeaderboardTable;
