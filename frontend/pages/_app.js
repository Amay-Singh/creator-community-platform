import { AuthProvider } from '../src/contexts/AuthContext';
import { SubscriptionProvider } from '../src/contexts/SubscriptionContext';
import { ThemeProvider } from '../src/components/ui/ThemeProvider';
import ErrorBoundary from '../src/components/Debug/ErrorBoundary';
import AuthGuard from '../src/components/AuthGuard';
import '../src/styles/index.css';

export default function App({ Component, pageProps }) {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <SubscriptionProvider>
            <AuthGuard>
              <Component {...pageProps} />
            </AuthGuard>
          </SubscriptionProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
