import React, { useMemo } from "react";
import Pagination from "./Pagination";
import RankBadge from "./RankBadge";
import SearchBar from "./SearchBar";
import defaultAvatar from "../assets/sample_user.png";

const GitHubIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="currentColor"
    className="github-icon"
  >
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
  </svg>
);

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
                        <a
                    href={`https://github.com/${contributor.username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="github-link"
                    title={`View ${contributor.username}'s GitHub profile`}
                  >
                    <GitHubIcon />
                  </a>
                      </div>
                    </td>
                    <td>{contributor.prsMerged}</td>
                    <td>{contributor.prsReviewed}</td>
                    <td>{contributor.issuesOpened}</td>
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
