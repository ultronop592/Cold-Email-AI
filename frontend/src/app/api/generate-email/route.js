const BACKEND_BASE_URL =
  process.env.BACKEND_API_URL || "http://127.0.0.1:8000";

function normalizeError(detail, fallback) {
  if (!detail) {
    return fallback;
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        const location = Array.isArray(item?.loc) ? item.loc.join(" -> ") : "field";
        return `${location}: ${item?.msg || JSON.stringify(item)}`;
      })
      .join(" | ");
  }

  if (typeof detail === "object") {
    return detail.message || JSON.stringify(detail);
  }

  return fallback;
}

export async function POST(request) {
  try {
    const formData = await request.formData();

    // Forward the real client IP so the backend rate limiter works per-user
    const clientIp =
      request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
      request.headers.get("x-real-ip") ||
      "unknown";

    const response = await fetch(`${BACKEND_BASE_URL}/generate-email`, {
      method: "POST",
      body: formData,
      headers: {
        "X-Forwarded-For": clientIp,
      },
    });

    const responseText = await response.text();
    let parsed;

    try {
      parsed = responseText ? JSON.parse(responseText) : {};
    } catch {
      parsed = { raw: responseText };
    }

    if (!response.ok) {
      const fallback = `Backend request failed with status ${response.status}`;
      return Response.json(
        {
          error: normalizeError(parsed?.detail || parsed?.error, fallback),
        },
        { status: response.status }
      );
    }

    return Response.json(parsed, { status: 200 });
  } catch (error) {
    return Response.json(
      {
        error:
          error?.message ||
          "Unable to reach backend API. Ensure FastAPI is running.",
      },
      { status: 500 }
    );
  }
}
