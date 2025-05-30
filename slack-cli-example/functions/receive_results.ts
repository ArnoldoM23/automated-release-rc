import { DefineFunction, Schema, SlackFunction } from "deno-slack-sdk/mod.ts";

export const ReceiveResultsFunction = DefineFunction({
  callback_id: "receive_results",
  title: "Receive Release Results",
  description: "Receive and display results from GitHub Actions",
  source_file: "functions/receive_results.ts",
  input_parameters: {
    properties: {
      success: {
        type: Schema.types.boolean,
        description: "Whether the workflow succeeded",
      },
      service_name: {
        type: Schema.types.string,
        description: "Service name",
      },
      version_from: {
        type: Schema.types.string,
        description: "Source version",
      },
      version_to: {
        type: Schema.types.string,
        description: "Target version",
      },
      artifacts_url: {
        type: Schema.types.string,
        description: "URL to download artifacts",
      },
      file_count: {
        type: Schema.types.integer,
        description: "Number of files generated",
      },
      total_size: {
        type: Schema.types.integer,
        description: "Total size of generated files",
      },
      pr_count: {
        type: Schema.types.integer,
        description: "Number of PRs processed",
      },
      channel_id: {
        type: Schema.slack.types.channel_id,
        description: "Channel to post results",
      },
      error_message: {
        type: Schema.types.string,
        description: "Error message if failed",
      },
    },
    required: ["success", "channel_id"],
  },
  output_parameters: {
    properties: {
      posted: {
        type: Schema.types.boolean,
        description: "Whether results were posted",
      },
    },
    required: ["posted"],
  },
});

export default SlackFunction(
  ReceiveResultsFunction,
  async ({ inputs, client }) => {
    try {
      let message: string;

      if (inputs.success) {
        // Success message with results
        message = `✅ **Release Documentation Generated Successfully!**

📋 **Results for ${inputs.service_name} ${inputs.version_from} → ${inputs.version_to}**

**Generated Files:**
• 📄 **${inputs.file_count} files** created
• 📊 **${inputs.total_size} bytes** of documentation
• 🔍 **${inputs.pr_count} PRs** analyzed

**Download Your Files:**
🔗 [Download Release Documentation](${inputs.artifacts_url})

**What You Got:**
• \`release_notes.txt\` - Confluence-ready release notes
• \`release_notes.md\` - GitHub markdown version  
• \`crq_day1.txt\` - Day 1 preparation CRQ
• \`crq_day2.txt\` - Day 2 deployment CRQ
• \`RELEASE_SUMMARY.md\` - Complete summary

🎉 **Ready to copy-paste into Confluence!**`;
      } else {
        // Error message
        message = `❌ **Release Documentation Generation Failed**

**Error:** ${inputs.error_message || "Unknown error occurred"}

**Troubleshooting:**
• Check GitHub repository access
• Verify version tags/commits exist
• Ensure GitHub token has proper permissions

🔗 [Check workflow logs](https://github.com/ArnoldoM23/automated-release-rc/actions)`;
      }

      // Post results message
      await client.chat.postMessage({
        channel: inputs.channel_id,
        text: message,
        mrkdwn: true,
      });

      return {
        outputs: {
          posted: true,
        },
      };
    } catch (error) {
      console.error("Error posting results:", error);
      return {
        outputs: {
          posted: false,
        },
      };
    }
  }
); 