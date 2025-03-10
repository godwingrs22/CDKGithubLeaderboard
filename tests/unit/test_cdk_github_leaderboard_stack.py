import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_github_leaderboard.cdk_github_leaderboard_stack import CdkGithubLeaderboardStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_github_leaderboard/cdk_github_leaderboard_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkGithubLeaderboardStack(app, "cdk-github-leaderboard")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
