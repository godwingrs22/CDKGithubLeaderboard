import React from 'react';
import defaultAvatar from '../assets/sample_user.png';
import RankBadge from './RankBadge';

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
                onError={(e) => e.target.src = defaultAvatar}
              />
            </div>
            <div className="username">{winners[1].username}</div>
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
                onError={(e) => e.target.src = defaultAvatar}
              />
            </div>
            <div className="username">{winners[0].username}</div>
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
                onError={(e) => e.target.src = defaultAvatar}
              />
            </div>
            <div className="username">{winners[2].username}</div>
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
