// useElectronChartResize.js - Custom hook for handling chart resize in Electron
import { useEffect } from 'react';

const useElectronChartResize = (chartRefs, dependencies = []) => {
  useEffect(() => {
    const resizeCharts = () => {
      setTimeout(() => {
        chartRefs.forEach(ref => {
          if (ref.current) {
            try {
              ref.current.resize();
            } catch (error) {
              console.warn('Chart resize error:', error);
            }
          }
        });
      }, 100);
    };

    const resizeChartsDelayed = () => {
      setTimeout(() => {
        chartRefs.forEach(ref => {
          if (ref.current) {
            try {
              ref.current.resize();
            } catch (error) {
              console.warn('Chart resize error:', error);
            }
          }
        });
      }, 300);
    };

    // Handle window resize
    window.addEventListener('resize', resizeCharts);
    
    // Handle Electron-specific events
    if (window.electron) {
      window.addEventListener('focus', resizeChartsDelayed);
      window.addEventListener('blur', resizeChartsDelayed);
      
      // Handle Electron window state changes
      const handleElectronEvents = () => {
        resizeChartsDelayed();
      };

      // Listen for visibility changes (minimize/restore)
      document.addEventListener('visibilitychange', handleElectronEvents);
      
      // Force resize on initial load for Electron
      setTimeout(resizeChartsDelayed, 500);
    }

    return () => {
      window.removeEventListener('resize', resizeCharts);
      if (window.electron) {
        window.removeEventListener('focus', resizeChartsDelayed);
        window.removeEventListener('blur', resizeChartsDelayed);
        document.removeEventListener('visibilitychange', handleElectronEvents);
      }
    };
  }, [chartRefs, ...dependencies]);

  // Effect to handle chart resize when dependencies change (like data updates)
  useEffect(() => {
    if (dependencies.some(dep => dep !== null && dep !== undefined)) {
      setTimeout(() => {
        chartRefs.forEach(ref => {
          if (ref.current) {
            try {
              ref.current.resize();
            } catch (error) {
              console.warn('Chart resize error:', error);
            }
          }
        });
      }, 400);
    }
  }, dependencies);
};

export default useElectronChartResize;
