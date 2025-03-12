import React from 'react';
import rank1Badge from '../assets/badges/rank1_badge.png';
import rank2Badge from '../assets/badges/rank2_badge.png';
import rank3Badge from '../assets/badges/rank3_badge.png';
import top20Badge from '../assets/badges/top20_badge.png';
import top50Badge from '../assets/badges/top50_badge.png';

function RankBadge({ rank }) {
  const getBadgeImage = (rank) => {
    if (rank === 1) return rank1Badge;
    if (rank === 2) return rank2Badge;
    if (rank === 3) return rank3Badge;
    if (rank >= 4 && rank <= 20) return top20Badge;
    if (rank >= 21 && rank <= 50) return top50Badge;
    return null;
  };

  const getBadgeTitle = (rank) => {
    if (rank === 1) return "Top Contributor";
    if (rank === 2) return "Silver Contributor";
    if (rank === 3) return "Bronze Contributor";
    if (rank >= 4 && rank <= 20) return "Elite Contributor";
    if (rank >= 21 && rank <= 50) return "Star Contributor";
    return "";
  };

  const badgeImage = getBadgeImage(rank);
  
  if (!badgeImage) return null;

  return (
    <img
      src={badgeImage}
      alt={`Rank ${rank} Badge`}
      title={getBadgeTitle(rank)}
      className="rank-badge"
    />
  );
}

export default RankBadge;
