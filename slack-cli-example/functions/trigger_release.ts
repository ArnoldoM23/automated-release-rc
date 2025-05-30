import { DefineFunction, Schema, SlackFunction } from "deno-slack-sdk/mod.ts";

export const TriggerReleaseFunction = DefineFunction({
  callback_id: "trigger_release",
  title: "Trigger Release Documentation",
  description: "Trigger GitHub Actions to generate release documentation",
  source_file: "functions/trigger_release.ts",
  input_parameters: {
    properties: {
      prod_version: {
        type: Schema.types.string,
        description: "Production version (e.g., v1.2.3)",
      },
      new_version: {
        type: Schema.types.string,
        description: "New release version (e.g., v1.3.0)",
      },
      service_name: {
        type: Schema.types.string,
        description: "Service name",
      },
      release_type: {
        type: Schema.types.string,
        description: "Release type",
      },
      rc_name: {
        type: Schema.types.string,
        description: "Release coordinator name",
      },
      rc_manager: {
        type: Schema.types.string,
        description: "Release manager name",
      },
      day1_date: {
        type: Schema.types.string,
        description: "Day 1 date",
      },
      day2_date: {
        type: Schema.types.string,
        description: "Day 2 date",
      },
      channel_id: {
        type: Schema.slack.types.channel_id,
        description: "Channel to post results",
      },
      user_id: {
        type: Schema.slack.types.user_id,
        description: "User who triggered release",
      },
    },
    required: [
      "prod_version",
      "new_version", 
      "service_name",
      "release_type",
      "rc_name",
      "rc_manager",
      "day1_date",
      "day2_date",
      "channel_id",
      "user_id"
    ],
  },
  output_parameters: {
    properties: {
      success: {
        type: Schema.types.boolean,
        description: "Whether the request was successful",
      },
      message: {
        type: Schema.types.string,
        description: "Status message",
      },
      workflow_url: {
        type: Schema.types.string,
        description: "GitHub Actions workflow URL",
      },
    },
    required: ["success", "message"],
  },
});

export default SlackFunction(
  TriggerReleaseFunction,
  async ({ inputs, env, client }) => {
    try {
      // Prepare payload for GitHub Actions
      const payload = {
        event_type: "run-release",
        client_payload: {
          prod_version: inputs.prod_version,
          new_version: inputs.new_version,
          service_name: inputs.service_name,
          release_type: inputs.release_type,
          rc_name: inputs.rc_name,
          rc_manager: inputs.rc_manager,
          day1_date: inputs.day1_date,
          day2_date: inputs.day2_date,
          slack_channel: `#${inputs.channel_id}`,
          slack_user: inputs.user_id,
          // Add webhook URL for results
          webhook_url: `${env.SLACK_WEBHOOK_URL}/webhook/release-results`
        }
      };

      // Make request to GitHub Actions
      const response = await fetch(
        "https://api.github.com/repos/ArnoldoM23/automated-release-rc/dispatches",
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (response.ok) {
        // Send initial confirmation message
        await client.chat.postMessage({
          channel: inputs.channel_id,
          text: `🚀 **Release automation started!**

**Service:** ${inputs.service_name} ${inputs.prod_version} → ${inputs.new_version}
**RC:** ${inputs.rc_name}
**Manager:** ${inputs.rc_manager}
**Type:** ${inputs.release_type}
**Schedule:** ${inputs.day1_date} (Day 1) → ${inputs.day2_date} (Day 2)

⏳ Generating release documentation...
📋 GitHub Actions workflow is running
🔗 Check progress: https://github.com/ArnoldoM23/automated-release-rc/actions

*Estimated completion: 30-60 seconds*
*Results will be posted when complete*`,
        });

        return {
          outputs: {
            success: true,
            message: "Release workflow triggered successfully",
            workflow_url: "https://github.com/ArnoldoM23/automated-release-rc/actions",
          },
        };
      } else {
        const errorText = await response.text();
        return {
          outputs: {
            success: false,
            message: `GitHub API error: ${response.status} - ${errorText}`,
          },
        };
      }
    } catch (error) {
      console.error("Error triggering release:", error);
      return {
        outputs: {
          success: false,
          message: `Error: ${error.message}`,
        },
      };
    }
  }
); 