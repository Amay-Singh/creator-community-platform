/**
 * Guardian Agent: SSR-safe client-only hook
 * Prevents hydration mismatches for client-only content
 */
import { useState, useEffect } from 'react';

export const useClientOnly = () => {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return isClient;
};

export default useClientOnly;
