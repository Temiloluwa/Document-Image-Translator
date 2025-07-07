import { NextRequest } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const filename = searchParams.get("filename");
  const target_language = searchParams.get("target_language");
  if (!filename || !target_language) {
    console.error("Missing filename or target_language", { filename, target_language });
    return new Response(JSON.stringify({ error: "filename and target_language are required" }), { status: 400 });
  }
  // Proxy to backend lambda/api endpoint
  const apiUrl = `${process.env.BACKEND_API_URL}/v1/presigned-url?filename=${encodeURIComponent(filename)}&target_language=${encodeURIComponent(target_language)}`;
  try {
    const res = await fetch(apiUrl, {
      headers: {
        "x-api-key": process.env.BACKEND_API_KEY || "",
      },
    });
    const data = await res.json();
    console.log("Lambda /v1/presigned-url response:", data);
    if (!res.ok) {
      console.error("Backend error (presigned-url)", { status: res.status, data });
    }
    return new Response(JSON.stringify(data), { status: res.status });
  } catch (err) {
    console.error("Fetch error (presigned-url)", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), { status: 500 });
  }
}
