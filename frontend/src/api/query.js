export default async function queryAPI(projectId, query) {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId, query })
    });
    if (!res.ok) {
      throw new Error("Failed to fetch query results");
    }
    return await res.json();
  }