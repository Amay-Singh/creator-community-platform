import { AuthProvider } from '../contexts/AuthContext';
import { SubscriptionProvider } from '../contexts/SubscriptionContext';
import { ThemeProvider } from '../components/ui/ThemeProvider';
import ErrorBoundary from '../components/Debug/ErrorBoundary';
import '../styles/index.css';

export default function App({ Component, pageProps }) {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <SubscriptionProvider>
            <Component {...pageProps} />
          </SubscriptionProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
