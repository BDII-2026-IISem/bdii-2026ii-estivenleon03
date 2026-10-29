import { Injectable, computed, signal } from '@angular/core';
import { EffectivePermission } from '../models/auth.model';

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  name?: string;
  isActive?: boolean;
  isStaff?: boolean;
  isSuperuser?: boolean;
}

export interface UserSession {
  user: UserProfile | null;
  accessToken: string | null;
  refreshToken: string | null;
  roles: string[];
  permissions: Array<EffectivePermission | string>;
}

@Injectable({ providedIn: 'root' })
export class SessionStore {
  private readonly STORAGE_KEY = 'storelab.session.v1';

  private readonly sessionState = signal<UserSession>(this.loadSession());

  readonly session = this.sessionState;
  readonly user = computed(() => this.sessionState().user);
  readonly accessToken = computed(() => this.sessionState().accessToken);
  readonly refreshToken = computed(() => this.sessionState().refreshToken);
  readonly roles = computed(() => this.sessionState().roles);
  readonly permissions = computed(() => this.sessionState().permissions);
  
  readonly permissionCount = computed(() => this.permissions().length);

  readonly isAuthenticated = computed(() => !!this.accessToken() && !!this.user());
  readonly isSuperuser = computed(() => !!this.user()?.isSuperuser || !!this.user()?.isStaff);

  canPermission(permission: string): boolean {
    const userObj = this.user();
    if (!userObj) return false;
    if (userObj.isSuperuser || userObj.isStaff) return true;

    const perms = this.permissions();
    const [method, ...pathParts] = permission.trim().split(/\s+/);
    if (!method || pathParts.length === 0) return perms.includes(permission);
    const requestedPath = normalizePermissionPath(pathParts.join(' '));

    return perms.some((granted) => {
      if (typeof granted === 'string') return granted === permission;
      if (granted.method.toUpperCase() !== method.toUpperCase()) return false;

      const grantedPath = normalizePermissionPath(granted.path);
      return pathsMatch(grantedPath, requestedPath);
    });
  }

  setTokens(tokens: { access: string; refresh?: string }): void {
    this.sessionState.update((current) => {
      const updated = {
        ...current,
        accessToken: tokens.access,
        refreshToken: tokens.refresh !== undefined ? tokens.refresh : current.refreshToken,
      };
      this.saveSession(updated);
      return updated;
    });
  }

  setUser(user: UserProfile, permissions: EffectivePermission[] = [], roles: string[] = []): void {
    this.sessionState.update((current) => {
      const updated = {
        ...current,
        user,
        permissions,
        roles: roles.length
          ? roles
          : [...new Set(permissions.map(({ roleName }) => roleName).filter(Boolean))],
      };
      this.saveSession(updated);
      return updated;
    });
  }

  setSession(sessionData: Partial<UserSession>): void {
    this.sessionState.update((current) => {
      const updated = { ...current, ...sessionData };
      this.saveSession(updated);
      return updated;
    });
  }

  clear(): void {
    const empty: UserSession = {
      user: null,
      accessToken: null,
      refreshToken: null,
      roles: [],
      permissions: [],
    };
    this.sessionState.set(empty);
    localStorage.removeItem(this.STORAGE_KEY);
  }

  private saveSession(session: UserSession): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(session));
  }

  private loadSession(): UserSession {
    const data = localStorage.getItem(this.STORAGE_KEY);
    if (!data) {
      return {
        user: null,
        accessToken: null,
        refreshToken: null,
        roles: [],
        permissions: [],
      };
    }
    try {
      const parsed = JSON.parse(data);
      if (parsed.username && !parsed.user) {
        return {
          user: {
            id: parsed.id,
            username: parsed.username,
            email: parsed.email,
            name: parsed.name,
            isActive: parsed.isActive,
            isStaff: parsed.isStaff,
            isSuperuser: parsed.isSuperuser,
          },
          accessToken: parsed.accessToken || parsed.access || null,
          refreshToken: parsed.refreshToken || parsed.refresh || null,
          roles: parsed.roles || [],
          permissions: parsed.permissions || [],
        };
      }
      return {
        user: parsed.user || null,
        accessToken: parsed.accessToken || null,
        refreshToken: parsed.refreshToken || null,
        roles: parsed.roles || [],
        permissions: parsed.permissions || [],
      };
    } catch {
      return {
        user: null,
        accessToken: null,
        refreshToken: null,
        roles: [],
        permissions: [],
      };
    }
  }

}

function normalizePermissionPath(path: string): string {
  const normalized = `/${path}`
    .replace(/\/+/g, '/')
    .replace(/\/$/, '')
    .replace(/^\/api\/v1(?=\/|$)/, '/api');
  return normalized || '/';
}

function pathsMatch(grantedPath: string, requestedPath: string): boolean {
  const grantedSegments = grantedPath.split('/');
  const requestedSegments = requestedPath.split('/');
  return (
    grantedSegments.length === requestedSegments.length &&
    grantedSegments.every(
      (segment, index) =>
        segment.startsWith(':') ||
        (segment.startsWith('<') && segment.endsWith('>')) ||
        segment === requestedSegments[index]
    )
  );
}
