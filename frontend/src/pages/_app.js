import { AuthProvider } from '../contexts/AuthContext';
import { SubscriptionProvider } from '../contexts/SubscriptionContext';
import ErrorBoundary from '../components/Debug/ErrorBoundary';

export default function App({ Component, pageProps }) {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <SubscriptionProvider>
          <Component {...pageProps} />
        </SubscriptionProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
