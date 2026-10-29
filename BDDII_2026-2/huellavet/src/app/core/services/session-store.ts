import { Injectable, computed, signal } from '@angular/core';

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
  permissions: any[];
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
    if (!perms || !Array.isArray(perms)) return true;
    
    return perms.some((p) => {
      if (!p) return false;
      if (typeof p === 'string') return p === permission;
      return p.name === permission || p.codename === permission;
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

  setUser(user: UserProfile, permissions: any[] = [], roles: string[] = []): void {
    this.sessionState.update((current) => {
      const updated = {
        ...current,
        user,
        permissions: permissions.length ? permissions : current.permissions,
        roles: roles.length ? roles : current.roles,
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
