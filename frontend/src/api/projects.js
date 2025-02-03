export default async function fetchProjects() {
    const res = await fetch("/api/projects");
    if (!res.ok) {
      throw new Error("Failed to fetch projects");
    }
    return await res.json();
  }