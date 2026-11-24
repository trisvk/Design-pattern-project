export type RealtimeEvent = {
  type: string
  payload: unknown
}

export type RealtimeHandler = (event: RealtimeEvent) => void

export function subscribeRealtime(handler: RealtimeHandler): () => void {
  void handler 
  return () => {
    
  }
}