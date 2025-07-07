import { NextRequest } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const htmlLoc = searchParams.get("html_results_location");
  const mdLoc = searchParams.get("markdown_results_location");
  let param = "";
  let value = "";
  if (htmlLoc) {
    param = "html_results_location";
    value = htmlLoc;
  } else if (mdLoc) {
    param = "markdown_results_location";
    value = mdLoc;
  } else {
    return new Response(JSON.stringify({ error: "A valid html_results_location or markdown_results_location is required" }), { status: 400 });
  }
  // Proxy to backend lambda/api endpoint
  const apiUrl = `${process.env.BACKEND_API_URL}/v1/result?${param}=${encodeURIComponent(value)}`;
  try {
    const res = await fetch(apiUrl, {
      headers: {
        "x-api-key": process.env.BACKEND_API_KEY || "",
      },
    });
    const data = await res.json();
    console.log("Lambda /v1/result response:", data);
    if (!res.ok) {
      console.error("Backend error (result)", { status: res.status, data });
    }
    return new Response(JSON.stringify(data), { status: res.status });
  } catch (err) {
    console.error("Fetch error (result)", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), { status: 500 });
  }
}
