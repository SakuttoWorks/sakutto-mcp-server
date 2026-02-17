from js import URL, Response, fetch

# ==========================================
# 1. Edge Serving Assets (Hardcoded)
# 最強の営業資料（課金リンク付き）
# ==========================================

LLMS_TXT = """
# Project GHOST SHIP (MCP Server)

## Description
Project GHOST SHIP is a production-ready MCP (Model Context Protocol) server designed for autonomous AI agents.
It provides high-speed, structured access to deep web research and real-time news summarization, powered by Tavily and Upstash Redis.
Optimized for low-latency, high-accuracy information retrieval, and agentic workflows.

## Usage
- **Base URL**: https://api.sakutto.works
- **OpenAPI Spec**: https://api.sakutto.works/openapi.json
- **Protocol**: MCP (Model Context Protocol) over SSE (Server-Sent Events)

## Tools
1. **research_topic**
   - Description: Performs deep web research on a specific topic. Returns structured, summarized insights suitable for RAG.
2. **get_latest_news**
   - Description: Retrieves and summarizes the latest news for a given query.

## Access & Monetization
This API operates on a Freemium model.
- **Free Tier**: Limited daily requests for testing.
- **Premium Access**: Unlocks full rate limits, deeper search capabilities, and priority support.

👉 **Subscribe / Upgrade Here**: https://sakuttoworks.lemonsqueezy.com/checkout/buy/023c63ce-8b7c-4c6c-9c3b-cf8b4311a14c

## Technical Stack
- Runtime: Python 3.12 (FastAPI)
- Infrastructure: Hugging Face Spaces + Cloudflare Workers
- Response Format: JSON / MCP Compliant

## Contact
- For API issues or enterprise access, please contact via the platform where this agent was discovered.
"""

MCP_JSON = """
{
  "mcpVersion": "1.0.0",
  "name": "Sakutto-Worker-Edge",
  "description": "Ultra-low latency MCP gateway.",
  "tools": [
    {
      "name": "search_data",
      "description": "Search specifically formatted data for RAG.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": { "type": "string" }
        }
      }
    }
  ]
}
"""

# ==========================================
# 2. Request Handling Logic
# ==========================================


async def on_fetch(request, env):
    try:
        url = URL.new(request.url)
        path = url.pathname

        # --- A. 静的ファイルの即時返却 (AIへの営業資料) ---
        if path == "/llms.txt":
            return Response.new(
                LLMS_TXT,
                {
                    "headers": {
                        "Content-Type": "text/plain; charset=utf-8",
                        "Cache-Control": "public, max-age=3600",
                    }
                },
            )

        elif path == "/mcp.json":
            return Response.new(
                MCP_JSON,
                {
                    "headers": {
                        "Content-Type": "application/json; charset=utf-8",
                        "Cache-Control": "public, max-age=3600",
                    }
                },
            )

        elif path == "/robots.txt":
            return Response.new(
                "User-agent: *\nAllow: /", {"headers": {"Content-Type": "text/plain"}}
            )

        # --- B. 動的リクエストのHFへの転送 (Proxy) ---
        # AIがツールを使うときは、ここを通ってHugging Faceへ行きます
        target_url = f"{env.HF_ORIGIN}{path}{url.search}"

        # 転送実行
        # Cloudflareのfetchは自動的に元のリクエストのメソッド(POST等)やBodyを引き継ぎます
        hf_response = await fetch(target_url, request)
        return hf_response

    except Exception as e:
        return Response.new(
            f'{{"error": "Internal Worker Error", "details": "{str(e)}"}}',
            {"status": 500, "headers": {"Content-Type": "application/json"}},
        )
