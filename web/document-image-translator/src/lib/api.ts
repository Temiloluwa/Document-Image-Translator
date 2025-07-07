
export async function getPresignedUrl(filename: string, targetLanguage: string) {
  const response = await fetch(`/api/v1/presigned-url?filename=${encodeURIComponent(filename)}&target_language=${encodeURIComponent(targetLanguage)}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function uploadFileToS3(file: File, uploadUrl: string) {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    body: file,
    headers: {
      "Content-Type": "application/octet-stream",
    },
  });
  if (!response.ok) {
    throw new Error(`Upload failed! status: ${response.status}`);
  }
  return true;
}



export async function checkProcessingStatus(resultLocation: string) {
  // resultLocation: html_results_location or markdown_results_location
  const param = resultLocation.endsWith('.html') ? 'html_results_location' : 'markdown_results_location';
  const url = `/api/v1/status?${param}=${encodeURIComponent(resultLocation)}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getResultUrls(resultLocation: string) {
  // resultLocation: html_results_location or markdown_results_location
  const param = resultLocation.endsWith('.html') ? 'html_results_location' : 'markdown_results_location';
  const url = `/api/v1/result?${param}=${encodeURIComponent(resultLocation)}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}
