'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';

// Define the Klaviyo LearnQ object on the window
declare global {
  interface Window {
    _learnq: any[];
  }
}

export function KlaviyoPageTracker() {
  const pathname = usePathname();

  useEffect(() => {
    // Ensure _learnq is initialized before pushing events
    if (typeof window._learnq !== 'undefined') {
      window._learnq.push(['track', 'Viewed Page', { Page: pathname }]);
    }
  }, [pathname]);

  return null; // This component does not render anything visible
}
