export default {
  // 定时任务触发入口
  async scheduled(event, env, ctx) {
    ctx.waitUntil(triggerGitHubActions(env));
  },

  // HTTP 访问手动触发，方便调试
  async fetch(request, env, ctx) {
    try {
      await triggerGitHubActions(env);
      return new Response("GitHub Actions trigger sent successfully!", { status: 200 });
    } catch (err) {
      return new Response(`Error: ${err.message}`, { status: 500 });
    }
  }
};

async function triggerGitHubActions(env) {
  const owner = env.GITHUB_OWNER; 
  const repo = env.GITHUB_REPO;
  const token = env.GITHUB_PAT; 

  if (!owner || !repo || !token) {
    throw new Error("Missing required environment variables in Worker: GITHUB_OWNER, GITHUB_REPO, and GITHUB_PAT must be configured.");
  }

  const url = `https://api.github.com/repos/${owner}/${repo}/dispatches`;
  
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "Cloudflare-Worker-OughtGather-Trigger",
      "X-GitHub-Api-Version": "2022-11-28"
    },
    body: JSON.stringify({
      event_type: "cf_trigger"
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`GitHub API error: ${response.status} - ${errorText}`);
  }
}
