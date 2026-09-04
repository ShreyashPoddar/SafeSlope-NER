/**
 * SafeSlope-NER — Auth Hook & Context
 * Provides a global auth state that persists across page navigations.
 * Restores session from localStorage JWT on app mount via GET /auth/me.
 */
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react';
import { getMe, demoLogin, logout as apiLogout, mapToUserProfile } from '../api/auth';
import type { DemoLoginPayload } from '../api/auth';
import type { UserProfile } from '../types/dashboard';

interface AuthContextValue {
  currentUser: UserProfile | null;
  isLoading: boolean;
  loginWithDemo: (payload: DemoLoginPayload) => Promise<UserProfile>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Restore session on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const me = await getMe();
        if (!cancelled && me) {
          setCurrentUser(mapToUserProfile(me));
        }
      } catch {
        // no valid session
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const loginWithDemo = useCallback(async (payload: DemoLoginPayload): Promise<UserProfile> => {
    const res = await demoLogin(payload);
    const profile = mapToUserProfile(res.user);
    setCurrentUser(profile);
    return profile;
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setCurrentUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ currentUser, isLoading, loginWithDemo, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used inside <AuthProvider>');
  }
  return ctx;
}
