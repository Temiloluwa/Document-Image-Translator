import type { Status } from "@/types";

export function pollStatus(uuid: string, fileName: string, onUpdate: (data: Status) => void) {
  const interval = setInterval(async () => {
    const res = await fetch(`/api/status?uuid=${encodeURIComponent(uuid)}&file_name=${encodeURIComponent(fileName)}`);
    if (res.ok) {
      const data = await res.json();
      onUpdate(data);
      if (data.status === "complete" && data.html_url) {
        clearInterval(interval);
      }
    }
  }, 2000);
  return interval;
}
