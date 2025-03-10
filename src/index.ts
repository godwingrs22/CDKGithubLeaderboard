import { graphql } from "@octokit/graphql";
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { MAINTAINERS } from './maintainers';

dotenv.config();

interface IssueNode {
  title: string;
  url: string;
  author: {
    login: string;
  };
  createdAt: string;
  state: string;
  labels: {
    nodes: Array<{
      name: string;
    }>;
  };
}

interface QueryResponse {
  repository: {
    issues: {
      nodes: IssueNode[];
      pageInfo: {
        hasNextPage: boolean;
        endCursor: string;
      };
    };
  };
}

interface AuthorStats {
  login: string;
  issueCount: number;
  issues: Array<{
    title: string;
    url: string;
    createdAt: string;
  }>;
}

const EXCLUDED_AUTHORS = ['github-actions', ...MAINTAINERS];
const EXCLUDED_LABELS = ['contribution/core'];

const fetchGithubIssues = async (): Promise<void> => {
  try {
    const graphqlWithAuth = graphql.defaults({
      headers: {
        authorization: `token ${process.env.GITHUB_TOKEN}`,
      },
    });

    let hasNextPage = true;
    let endCursor: string | null = null;
    const allIssues: IssueNode[] = [];

    while (hasNextPage) {
      const query = `
        query($cursor: String) {
          repository(owner: "aws", name: "aws-cdk") {
            issues(
              first: 100,
              after: $cursor,
              orderBy: {field: CREATED_AT, direction: DESC},
              filterBy: {since: "2024-01-01T00:00:00Z"}
            ) {
              nodes {
                title
                url
                author {
                  login
                }
                createdAt
                state
                labels(first: 100) {
                  nodes {
                    name
                  }
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
      `;

      const response: QueryResponse = await graphqlWithAuth(query, {
        cursor: endCursor,
      });

      allIssues.push(...response.repository.issues.nodes);
      hasNextPage = response.repository.issues.pageInfo.hasNextPage;
      endCursor = response.repository.issues.pageInfo.endCursor;
    }

    // Filter out issues from maintainers, excluded authors, and labels
    const filteredIssues = allIssues.filter(issue => {
      const issueLabels = issue.labels.nodes.map(label => label.name);
      return (
        issue.author &&
        !EXCLUDED_AUTHORS.includes(issue.author.login) &&
        !issueLabels.some(label => EXCLUDED_LABELS.includes(label))
      );
    });

    // Group issues by author
    const authorStats = new Map<string, AuthorStats>();

    filteredIssues.forEach((issue) => {
      if (!issue.author) return;

      const authorLogin = issue.author.login;
      if (!authorStats.has(authorLogin)) {
        authorStats.set(authorLogin, {
          login: authorLogin,
          issueCount: 0,
          issues: [],
        });
      }

      const stats = authorStats.get(authorLogin)!;
      stats.issueCount++;
      stats.issues.push({
        title: issue.title,
        url: issue.url,
        createdAt: issue.createdAt,
      });
    });

    // Sort authors by issue count (descending)
    const sortedAuthors = Array.from(authorStats.values())
      .sort((a, b) => b.issueCount - a.issueCount);

    // Create CSV content
    const csvHeader = 'Rank,Author,Issues Created,Latest Issue,Latest Issue Date,Latest Issue URL\n';
    const csvRows = sortedAuthors.map((author, index) => {
      const latestIssue = author.issues[0] || { title: '', createdAt: '', url: '' };
      return `${index + 1},"${author.login}",${author.issueCount},"${latestIssue.title.replace(/"/g, '""')}","${new Date(latestIssue.createdAt).toLocaleDateString()}","${latestIssue.url}"`;
    });

    const csvContent = csvHeader + csvRows.join('\n');

    // Create output directory if it doesn't exist
    const outputDir = path.join(__dirname, '..', 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir);
    }

    // Generate filename with current date
    const currentDate = new Date().toISOString().split('T')[0];
    const fileName = `aws-cdk-external-contributors-${currentDate}.csv`;
    const filePath = path.join(outputDir, fileName);

    // Write to CSV file
    fs.writeFileSync(filePath, csvContent);

    // Console output
    console.log('\nAWS CDK External Contributors Statistics (Since January 1st, 2024)');
    console.log('===========================================================');
    console.log(`Total issues analyzed: ${allIssues.length}`);
    console.log(`External contributor issues: ${filteredIssues.length}`);
    console.log(`Unique external contributors: ${authorStats.size}`);
    console.log(`\nExcluded:`);
    console.log(`- Labels: ${EXCLUDED_LABELS.join(', ')}`);
    console.log(`- Maintainers & System: ${EXCLUDED_AUTHORS.length} users`);
    console.log(`\nData has been exported to: ${filePath}`);

  } catch (error) {
    console.error('Error fetching issues:', error);
  }
};

// Execute the function
fetchGithubIssues();
