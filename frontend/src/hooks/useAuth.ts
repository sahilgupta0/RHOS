import { useAuth as useAuthContext } from "../context/AuthContext";

/**
 * Hook to access the Authentication Context state and actions.
 */
export function useAuth() {
  return useAuthContext();
}
