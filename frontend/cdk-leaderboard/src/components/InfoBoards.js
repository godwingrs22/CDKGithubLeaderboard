import React from 'react';
import rank1Badge from '../assets/badges/rank1_badge.png';
import rank2Badge from '../assets/badges/rank2_badge.png';
import rank3Badge from '../assets/badges/rank3_badge.png';
import top20Badge from '../assets/badges/top20_badge.png';
import top50Badge from '../assets/badges/top50_badge.png';
import top100Badge from '../assets/badges/top100_badge.png';

const PRMergedIcon = () => (
    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
      <path d="M5 3.254V3.25v.005a.75.75 0 110-.005v.004zm.45 1.9a2.25 2.25 0 10-1.95.218v5.256a2.25 2.25 0 101.5 0V7.123A5.735 5.735 0 009.25 9h1.378a2.251 2.251 0 100-1.5H9.25a4.25 4.25 0 01-3.8-2.346zM12.75 9a.75.75 0 100-1.5.75.75 0 000 1.5zm-8.5-6.5a.75.75 0 100-1.5.75.75 0 000 1.5z" />
    </svg>
  );
  
  const PRReviewedIcon = () => (
    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
      <path d="M2.5 1.75a.25.25 0 01.25-.25h8.5a.25.25 0 01.25.25v7.736a.75.75 0 101.5 0V1.75A1.75 1.75 0 0011.25 0h-8.5A1.75 1.75 0 001 1.75v11.5c0 .966.784 1.75 1.75 1.75h3.17a.75.75 0 000-1.5H2.75a.25.25 0 01-.25-.25V1.75z" />
      <path d="M4.75 12.5a.75.75 0 000 1.5h4.5a.75.75 0 000-1.5h-4.5z" />
    </svg>
  );
  
  const IssueCreatedIcon = () => (
    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
      <path d="M8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z" />
    </svg>
  );
  
  const DiscussionAnsweredIcon = () => (
    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
      <path d="M1.5 2.75a.25.25 0 01.25-.25h8.5a.25.25 0 01.25.25v5.5a.25.25 0 01-.25.25h-3.5a.75.75 0 00-.53.22L3.5 11.44V9.25a.75.75 0 00-.75-.75h-1a.25.25 0 01-.25-.25v-5.5z" />
      <path d="M11.5 2.75a.25.25 0 01.25-.25h8.5a.25.25 0 01.25.25v5.5a.25.25 0 01-.25.25h-3.5a.75.75 0 00-.53.22L13.5 11.44V9.25a.75.75 0 00-.75-.75h-1a.25.25 0 01-.25-.25v-5.5z" />
    </svg>
  );

const InfoBoards = () => {
    return (
      <div className="info-boards">
        <div className="info-board scoring">
          <h3>Scoring Calculation</h3>
          <ul>
          <li>
            <PRMergedIcon />
            <span>PR Merged: 10 points</span>
          </li>
          <li>
            <PRReviewedIcon />
            <span>PR Reviewed: 8 points</span>
          </li>
          <li>
            <IssueCreatedIcon />
            <span>Issue Created: 5 points</span>
          </li>
          <li>
            <DiscussionAnsweredIcon />
            <span>Discussion Answered: 3 points</span>
          </li>
        </ul>
        </div>
        <div className="info-board badges">
          <h3>Badge Levels</h3>
          <ul>
          <li>
            <img src={rank1Badge} alt="Rank 1" className="info-badge" />
            <span>Rank 1: Top Contributor</span>
          </li>
          <li>
            <img src={rank2Badge} alt="Rank 2" className="info-badge" />
            <span>Rank 2: Silver Contributor</span>
          </li>
          <li>
            <img src={rank3Badge} alt="Rank 3" className="info-badge" />
            <span>Rank 3: Bronze Contributor</span>
          </li>
          <li>
            <img src={top20Badge} alt="Top 20" className="info-badge" />
            <span>Ranks 4-20: Elite Contributor</span>
          </li>
          <li>
            <img src={top50Badge} alt="Top 50" className="info-badge" />
            <span>Ranks 21-50: Star Contributor</span>
          </li>
          <li>
            <img src={top100Badge} alt="Top 100" className="info-badge" />
            <span>Ranks 51-100: Rising Contributor</span>
          </li>
        </ul>
        </div>
      </div>
    );
  };
  
  export default InfoBoards;