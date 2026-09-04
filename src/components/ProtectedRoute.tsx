import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import type { UserProfile } from '../types/dashboard';

interface ProtectedRouteProps {
  children: React.ReactElement;
  currentUser: UserProfile | null;
  allowedRoles?: string[];
  requireHeadAdmin?: boolean;
  onUnauthorizedToast?: (msg: string) => void;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  currentUser,
  allowedRoles = [],
  requireHeadAdmin = false,
  onUnauthorizedToast
}) => {
  const location = useLocation();

  // Rule 1 (Portal Gate): If the route requires administrative privileges and user is logged in as portalType === 'User' or null, block access immediately
  const isLoggedOutOrUser = !currentUser || currentUser.portalType === 'user';

  // Rule 2 (Head Admin Privilege): If adminType === 'Head Admin', allow access to ALL routes without exception
  const isHeadAdmin = currentUser?.persona === 'head_admin' || currentUser?.subRole === 'Head Admin';

  // Rule 3 (Role-Based Sub-Role Gate): If adminType === 'Role-Based Admin', allow access ONLY if the user's specific subRole matches allowedRoles
  const isSubRoleAllowed = currentUser?.subRole && allowedRoles.includes(currentUser.subRole);

  const isAuthorized = isHeadAdmin || (!requireHeadAdmin && !isLoggedOutOrUser && isSubRoleAllowed);

  useEffect(() => {
    if (!isAuthorized && onUnauthorizedToast) {
      onUnauthorizedToast('🔒 Access Restricted: Administrative authorization required.');
    }
  }, [isAuthorized, onUnauthorizedToast]);

  if (!isAuthorized) {
    return (
      <Navigate 
        to="/login" 
        state={{ from: location, accessWarning: '🔒 Access Restricted: Administrative authorization required.' }} 
        replace 
      />
    );
  }

  return children;
};
