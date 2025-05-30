import { DefineFunction, Schema, SlackFunction } from "deno-slack-sdk/mod.ts";

export const MessagePRAuthorsFunction = DefineFunction({
  callback_id: "message_pr_authors",
  title: "Message PR Authors",
  description: "Send messages to PR authors for sign-off requests",
  source_file: "functions/message_pr_authors.ts",
  input_parameters: {
    properties: {
      pr_authors: {
        type: Schema.types.array,
        items: {
          type: Schema.types.object,
          properties: {
            slack_id: { type: Schema.slack.types.user_id },
            pr_number: { type: Schema.types.integer },
            pr_title: { type: Schema.types.string },
            pr_url: { type: Schema.types.string },
          },
        },
        description: "Array of PR authors to message",
      },
      service_name: {
        type: Schema.types.string,
        description: "Service name",
      },
      release_version: {
        type: Schema.types.string,
        description: "Release version",
      },
      cutoff_date: {
        type: Schema.types.string,
        description: "Sign-off cutoff date",
      },
      channel_id: {
        type: Schema.slack.types.channel_id,
        description: "Release coordination channel",
      },
    },
    required: ["pr_authors", "service_name", "release_version", "channel_id"],
  },
  output_parameters: {
    properties: {
      messages_sent: {
        type: Schema.types.integer,
        description: "Number of messages sent",
      },
      failed_messages: {
        type: Schema.types.integer,
        description: "Number of failed messages",
      },
    },
    required: ["messages_sent", "failed_messages"],
  },
});

export default SlackFunction(
  MessagePRAuthorsFunction,
  async ({ inputs, client }) => {
    let messagesSent = 0;
    let failedMessages = 0;

    for (const author of inputs.pr_authors) {
      try {
        // Send DM to each PR author
        await client.chat.postMessage({
          channel: author.slack_id,
          text: `🚀 **Release Sign-off Required**

Hi! Your PR is included in the upcoming release of **${inputs.service_name} ${inputs.release_version}**.

**Your PR:**
• **#${author.pr_number}**: ${author.pr_title}
• **Link**: ${author.pr_url}

**🎯 Action Required:**
Please confirm your PR is ready for release by replying in the release channel:

👉 Go to <#${inputs.channel_id}> and comment: \`✅ PR #${author.pr_number} signed off\`

**⏰ Cutoff:** ${inputs.cutoff_date || "12:00 PM tomorrow"}

Thanks for your contribution to this release! 🙌`,
          mrkdwn: true,
        });

        messagesSent++;
        
        // Also mention them in the main channel
        await client.chat.postMessage({
          channel: inputs.channel_id,
          text: `📢 <@${author.slack_id}> - Please sign off on PR #${author.pr_number}: ${author.pr_title}`,
          thread_ts: undefined, // Post as new message, not in thread
        });

      } catch (error) {
        console.error(`Failed to message ${author.slack_id}:`, error);
        failedMessages++;
      }
    }

    // Post summary to coordination channel
    await client.chat.postMessage({
      channel: inputs.channel_id,
      text: `📨 **PR Author Notifications Sent**

✅ **${messagesSent}** developers notified
${failedMessages > 0 ? `❌ **${failedMessages}** messages failed` : ""}

**Waiting for sign-offs on:**
${inputs.pr_authors.map(author => 
  `• <@${author.slack_id}> - PR #${author.pr_number}`
).join('\n')}

**Cutoff:** ${inputs.cutoff_date || "12:00 PM tomorrow"}

Reply with: \`✅ PR #XXX signed off\` to confirm your PRs.`,
      mrkdwn: true,
    });

    return {
      outputs: {
        messages_sent: messagesSent,
        failed_messages: failedMessages,
      },
    };
  }
); 