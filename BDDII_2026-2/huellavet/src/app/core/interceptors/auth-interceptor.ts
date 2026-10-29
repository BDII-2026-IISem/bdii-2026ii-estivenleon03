import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, finalize, shareReplay, switchMap, throwError } from 'rxjs';
import { TokenPair } from '../models/auth.model';
import { AuthService } from '../services/auth';
import { NotificationService } from '../services/notification.service';
import { SessionStore } from '../services/session-store';

let refreshInFlight: Observable<TokenPair> | null = null;
const TOKEN_ENDPOINTS = ['/auth/login/', '/auth/refresh/', '/auth/logout/'];

function redirectToLogin(session: SessionStore, router: Router, notify: NotificationService): void {
  session.clear();
  notify.error('Sesión vencida', 'Vuelve a iniciar sesión.');
  const returnUrl = router.url.startsWith('/login') ? '/dashboard' : router.url;
  void router.navigate(['/login'], { queryParams: { returnUrl } });
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const session = inject(SessionStore);
  const auth = inject(AuthService);
  const router = inject(Router);
  const notify = inject(NotificationService);

  const isTokenEndpoint = TOKEN_ENDPOINTS.some((endpoint) => req.url.includes(endpoint));
  const access = session.accessToken();

  const request =
    access && !isTokenEndpoint
      ? req.clone({ setHeaders: { Authorization: `Bearer ${access}` } })
      : req;

  return next(request).pipe(
    catchError((error: unknown) => {
      if (!(error instanceof HttpErrorResponse) || error.status !== 401 || isTokenEndpoint) {
        return throwError(() => error);
      }

      if (!session.refreshToken()) {
        redirectToLogin(session, router, notify);
        return throwError(() => error);
      }

      refreshInFlight ??= auth.refresh().pipe(
        catchError((refreshError: unknown) => {
          redirectToLogin(session, router, notify);
          return throwError(() => refreshError);
        }),
        finalize(() => {
          refreshInFlight = null;
        }),
        shareReplay({ bufferSize: 1, refCount: false })
      );

      return refreshInFlight.pipe(
        switchMap(() => {
          const renewed = session.accessToken();
          return next(
            renewed ? req.clone({ setHeaders: { Authorization: `Bearer ${renewed}` } }) : req
          );
        })
      );
    })
  );
};
