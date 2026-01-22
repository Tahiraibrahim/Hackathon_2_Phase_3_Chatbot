import { StreamingTextResponse } from "ai";

// IMPORTANT: Runtime must be nodejs for localhost communication
export const runtime = "nodejs";

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

    // 1. Extract session token from multiple sources
    // Priority: Authorization header > X-Session-Token header > Cookie
    let sessionToken: string | null = null;
    let tokenSource = "none";

    // Check Authorization header first (Bearer token)
    const authHeader = req.headers.get("authorization");
    if (authHeader && authHeader.startsWith("Bearer ")) {
      sessionToken = authHeader.substring(7);
      tokenSource = "Authorization Header";
    }

    // Fallback to X-Session-Token header
    if (!sessionToken) {
      const xSessionToken = req.headers.get("x-session-token");
      if (xSessionToken) {
        sessionToken = xSessionToken;
        tokenSource = "X-Session-Token Header";
      }
    }

    // CRITICAL FALLBACK: Read from cookie if headers don't have token
    if (!sessionToken) {
      const cookieHeader = req.headers.get("cookie");
      if (cookieHeader) {
        // Try multiple cookie name patterns
        const patterns = [
          /better-auth\.session_token=([^;]+)/,
          /session_token=([^;]+)/,
          /authjs\.session-token=([^;]+)/,
        ];

        for (const pattern of patterns) {
          const match = cookieHeader.match(pattern);
          if (match && match[1]) {
            // Decode URL-encoded token (fixes %3D and other encoding issues)
            sessionToken = decodeURIComponent(match[1]);
            tokenSource = `Cookie (${pattern.source})`;
            break;
          }
        }
      }
    }

    console.log("--- CHAT API DEBUG ---");
    console.log("Authorization Header:", authHeader || "missing");
    console.log("Cookie Header:", req.headers.get("cookie") ? "present" : "missing");
    console.log("Session Token Present:", !!sessionToken);
    console.log("Token Source:", tokenSource);
    console.log("Token Length:", sessionToken?.length || 0);

    // 2. Require authentication - BLOCK if no token found
    if (!sessionToken) {
      console.error("❌ CRITICAL: No Session Token found in Authorization header, X-Session-Token header, or cookies");
      return new Response(JSON.stringify({
        detail: "Missing authentication token. Please ensure you are logged in.",
        debug: {
          authHeader: !!authHeader,
          cookieHeader: !!req.headers.get("cookie"),
          checkedSources: ["Authorization", "X-Session-Token", "Cookies"]
        }
      }), {
        status: 401,
        headers: { "Content-Type": "application/json" }
      });
    }

    // Get the last message
    const lastMessage = messages[messages.length - 1];

    // 3. Prepare headers for Python Backend
    const backendHeaders: Record<string, string> = {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${sessionToken}`,
    };

    console.log("Forwarding to Backend with token...");

    // 4. Forward to Python Backend
    const response = await fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: backendHeaders,
      body: JSON.stringify({
        message: lastMessage.content,
        conversation_id: null,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Python Backend Error:", response.status, errorText);
      return new Response(errorText, { status: response.status });
    }

    // 5. Safe JSON parsing to handle truncated responses
    let data;
    try {
      // Get raw text first for debugging
      const rawText = await response.text();
      console.log("📊 Response length:", rawText.length, "bytes");

      // Attempt to parse JSON
      data = JSON.parse(rawText);
    } catch (parseError) {
      console.error("❌ JSON Parse Error:", parseError);
      console.error("Response was incomplete or malformed");
      return new Response(
        JSON.stringify({
          detail: "Server response was incomplete. Please try again.",
          error: "JSON_PARSE_ERROR"
        }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // 6. Stream the response in AI SDK protocol format
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        const text = data.response || "";
        // Format according to AI SDK Data Stream Protocol
        // Protocol format: 0:"text content"\n for text chunks
        // Use JSON.stringify to properly escape all special characters (quotes, newlines, backslashes, etc.)
        controller.enqueue(encoder.encode(`0:${JSON.stringify(text)}\n`));
        controller.close();
      },
    });

    return new StreamingTextResponse(stream);

  } catch (error) {
    console.error("🔥 Chat API Critical Error:", error);
    return new Response(
      JSON.stringify({ detail: "Internal Server Error" }), 
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}