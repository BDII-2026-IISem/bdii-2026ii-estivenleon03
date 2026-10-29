import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { EffectivePermission } from '../../../core/models/auth.model';
import { User, UserPayload } from '../../../core/models/user.model';
import { CrudService } from '../crud';

@Injectable({ providedIn: 'root' })
export class UserApi extends CrudService<User, UserPayload> {
  constructor() {
    super(`${environment.apiUrl}/users`);
  }

  permissions(id: number): Observable<EffectivePermission[]> {
    return this.http
      .get<{ permissions: EffectivePermission[] }>(`${this.endpoint}/${id}/permissions/`)
      .pipe(map((res) => res.permissions));
  }
}
