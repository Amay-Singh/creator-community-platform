import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

/**
 * AuthGuard Component
 * Protects routes by checking authentication status
 * Redirects to login if not authenticated
 */
export default function AuthGuard({ children }) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Define public routes that don't require authentication
  const publicRoutes = ['/', '/login', '/register'];
  
  // Check if current route is public
  const isPublicRoute = publicRoutes.includes(router.pathname);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if user has token
        const token = localStorage.getItem('token');
        
        if (!token) {
          setIsAuthenticated(false);
          setIsLoading(false);
          
          // Redirect to login if trying to access protected route
          if (!isPublicRoute) {
            router.push('/login');
          }
          return;
        }

        // Validate token with backend
        const response = await fetch('https://creator-platform-backend-vfuz.onrender.com/api/accounts/profile/', {
          headers: {
            'Authorization': `Token ${token}`
          }
        });

        if (response.ok) {
          setIsAuthenticated(true);
        } else {
          // Token is invalid, remove it
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setIsAuthenticated(false);
          
          // Redirect to login if trying to access protected route
          if (!isPublicRoute) {
            router.push('/login');
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsAuthenticated(false);
        
        // Redirect to login if trying to access protected route
        if (!isPublicRoute) {
          router.push('/login');
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router.pathname, isPublicRoute, router]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // For public routes, always show content
  if (isPublicRoute) {
    return children;
  }

  // For protected routes, only show if authenticated
  if (isAuthenticated) {
    return children;
  }

  // Show loading while redirecting to login
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirecting to login...</p>
      </div>
    </div>
  );
}
