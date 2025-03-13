import React from "react";
import defaultAvatar from "../assets/sample_user.png";
import RankBadge from "./RankBadge";

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

function TopThree({ winners }) {
  const getGithubAvatar = (username) => `https://github.com/${username}.png`;

  return (
    <div className="top-three">
      <div className="winner second">
        {winners[1] && (
          <>
            <div className="circle">
              <img
                src={getGithubAvatar(winners[1].username)}
                alt="avatar"
                className="winner-avatar"
                onError={(e) => (e.target.src = defaultAvatar)}
              />
            </div>
            <div className="username">
              {winners[1].username}
              <a
                href={`https://github.com/${winners[1].username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="github-link"
                title={`View ${winners[1].username}'s GitHub profile`}
              >
                <GitHubIcon />
              </a>
            </div>
            <div className="score">{winners[1].totalScore}</div>
            <RankBadge rank={2} />
            <div className="rank-number">2</div>
          </>
        )}
      </div>
      <div className="winner first">
        {winners[0] && (
          <>
            <div className="circle">
              <img
                src={getGithubAvatar(winners[0].username)}
                alt="avatar"
                className="winner-avatar"
                onError={(e) => (e.target.src = defaultAvatar)}
              />
            </div>
            <div className="username">
              {winners[0].username}
              <a
                href={`https://github.com/${winners[0].username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="github-link"
                title={`View ${winners[0].username}'s GitHub profile`}
              >
                <GitHubIcon />
              </a>
            </div>
            <div className="score">{winners[0].totalScore}</div>
            <RankBadge rank={1} />
            <div className="rank-number">1</div>
          </>
        )}
      </div>
      <div className="winner third">
        {winners[2] && (
          <>
            <div className="circle">
              <img
                src={getGithubAvatar(winners[2].username)}
                alt="avatar"
                className="winner-avatar"
                onError={(e) => (e.target.src = defaultAvatar)}
              />
            </div>
            <div className="username">
              {winners[2].username}
              <a
                href={`https://github.com/${winners[2].username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="github-link"
                title={`View ${winners[2].username}'s GitHub profile`}
              >
                <GitHubIcon />
              </a>
            </div>
            <div className="score">{winners[2].totalScore}</div>
            <RankBadge rank={3} />
            <div className="rank-number">3</div>
          </>
        )}
      </div>
    </div>
  );
}

export default TopThree;
