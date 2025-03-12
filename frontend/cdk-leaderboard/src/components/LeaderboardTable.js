import React from 'react';
import Pagination from './Pagination';
import RankBadge from './RankBadge';
import defaultAvatar from '../assets/sample_user.png';

function LeaderboardTable({ data }) {
  const [currentPage, setCurrentPage] = React.useState(1);
  const itemsPerPage = 20;
  
  // Skip the first 3 entries as they're shown in TopThree
  const remainingContributors = data.slice(3);
  const totalPages = Math.ceil(remainingContributors.length / itemsPerPage);
  
  // Calculate the current page's data
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentData = remainingContributors.slice(startIndex, endIndex);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    // Scroll to top of table
    document.querySelector('.table-container').scrollIntoView({
      behavior: 'smooth'
    });
  };

  return (
    <div className="leaderboard-section">
      <div className="table-container">
        <table className="leaderboard-table">
          <thead>
            <tr>
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
              const actualRank = startIndex + index + 4; // +4 because we skipped top 3
              return (
                <tr key={contributor.username}>
                  <td>
                    <div className="rank-cell">
                      <span>{actualRank}</span>
                      <RankBadge rank={actualRank} />
                    </div>
                  </td>
                  <td>
                    <div className="user-cell">
                      <img 
                        src={contributor.imageUrl || defaultAvatar} 
                        alt="avatar"
                        className="avatar"
                        onError={(e) => e.target.src = defaultAvatar}
                      />
                      <span>{contributor.username}</span>
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
