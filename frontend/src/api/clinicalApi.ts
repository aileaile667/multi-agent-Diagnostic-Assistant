import type {
  AnalyzeRequest,
  AnalyzeResponse,
  DDICheckResponse,
  HealthResponse,
  ICD10LookupResponse,
  ICD10SearchResponse,
  StreamEvent,
} from "@/types/clinical";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function parseSseFrame(frame: string): StreamEvent | null {
  const dataLine = frame
    .split("\n")
    .find((line) => line.startsWith("data:"));

  if (!dataLine) {
    return null;
  }

  return JSON.parse(dataLine.slice(5).trim()) as StreamEvent;
}

export async function analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  return requestJson<AnalyzeResponse>(`${API_BASE}/clinical/analyze`, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function streamAnalyze(
  request: AnalyzeRequest,
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const response = await fetch(`${API_BASE}/clinical/analyze/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok || !response.body) {
    throw new Error(`Stream failed with ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const event = parseSseFrame(frame);
      if (event) {
        onEvent(event);
      }
    }
  }

  if (buffer.trim()) {
    const event = parseSseFrame(buffer);
    if (event) {
      onEvent(event);
    }
  }
}

export async function searchICD10(query: string): Promise<ICD10SearchResponse> {
  return requestJson<ICD10SearchResponse>(`${API_BASE}/clinical/icd10/search`, {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export async function getICD10(code: string): Promise<ICD10LookupResponse> {
  return requestJson<ICD10LookupResponse>(
    `${API_BASE}/clinical/icd10/${encodeURIComponent(code)}`,
  );
}

export async function checkDDI(
  newDrugs: string[],
  currentDrugs: string[],
): Promise<DDICheckResponse> {
  return requestJson<DDICheckResponse>(`${API_BASE}/clinical/ddi/check`, {
    method: "POST",
    body: JSON.stringify({
      new_drugs: newDrugs,
      current_drugs: currentDrugs,
    }),
  });
}

export async function health(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/health");
}
