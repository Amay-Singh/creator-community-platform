import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import NotificationBell from './ui/NotificationBell';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-[var(--color-neutral-50)]">
      {/* Header */}
      <header className="
        bg-white border-b border-[var(--color-neutral-200)]
        sticky top-0 z-40
      ">
        <div className="max-w-7xl mx-auto px-[var(--spacing-4)]">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <a
                href="/"
                className="
                  text-[var(--font-size-xl)] font-bold text-[var(--color-primary-600)]
                  hover:text-[var(--color-primary-700)]
                  transition-colors duration-[var(--duration-fast)]
                "
              >
                Creator Platform
              </a>
            </div>

            {/* Navigation */}
            {user && (
              <nav className="hidden md:flex items-center space-x-[var(--spacing-6)]">
                <a
                  href="/search"
                  className="
                    text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]
                    transition-colors duration-[var(--duration-fast)]
                  "
                >
                  Search
                </a>
                <a
                  href="/feed"
                  className="
                    text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]
                    transition-colors duration-[var(--duration-fast)]
                  "
                >
                  Feed
                </a>
                <a
                  href="/chat"
                  className="
                    text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]
                    transition-colors duration-[var(--duration-fast)]
                  "
                >
                  Chat
                </a>
              </nav>
            )}

            {/* User Actions */}
            <div className="flex items-center space-x-[var(--spacing-3)]">
              {user ? (
                <>
                  <NotificationBell />
                  <div className="flex items-center space-x-[var(--spacing-3)]">
                    <a
                      href="/profile"
                      className="
                        text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]
                        transition-colors duration-[var(--duration-fast)]
                      "
                    >
                      Profile
                    </a>
                    <button
                      onClick={logout}
                      className="
                        text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]
                        transition-colors duration-[var(--duration-fast)]
                      "
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex items-center space-x-[var(--spacing-3)]">
                  <a
                    href="/auth/login"
                    className="
                      text-[var(--color-neutral-600)] hover:text-[var(--color-neutral-900)]
                      transition-colors duration-[var(--duration-fast)]
                    "
                  >
                    Login
                  </a>
                  <a
                    href="/auth/register"
                    className="
                      bg-[var(--color-primary-600)] text-white
                      px-[var(--spacing-4)] py-[var(--spacing-2)]
                      rounded-[var(--radius-base)]
                      hover:bg-[var(--color-primary-700)]
                      transition-colors duration-[var(--duration-fast)]
                    "
                  >
                    Sign Up
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {children}
      </main>
    </div>
  );
};

export default Layout;
