import { CanActivateFn } from '@angular/router';

export const authOnlyGuard: CanActivateFn = (route, state) => {
  return true;
};
