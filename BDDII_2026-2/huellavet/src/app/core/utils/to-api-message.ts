export function toApiMessage(error: unknown): string {
  if (error && typeof error === 'object') {
    const errObj = error as Record<string, unknown>;
    if (typeof errObj['error'] === 'string') {
      return errObj['error'];
    }
    if (errObj['error'] && typeof errObj['error'] === 'object') {
      const inner = errObj['error'] as Record<string, unknown>;
      if (typeof inner['detail'] === 'string') return inner['detail'];
      const firstKey = Object.keys(inner)[0];
      if (firstKey && Array.isArray(inner[firstKey])) {
        return `${firstKey}: ${(inner[firstKey] as string[])[0]}`;
      }
    }
    if (typeof errObj['detail'] === 'string') {
      return errObj['detail'];
    }
    if (typeof errObj['message'] === 'string') {
      return errObj['message'];
    }
  }
  return 'Ocurrió un error inesperado en la solicitud.';
}
