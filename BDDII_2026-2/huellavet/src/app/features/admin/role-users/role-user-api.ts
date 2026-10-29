import { Injectable } from '@angular/core';
import { environment } from '../../../../environments/environment';
import { RoleUser, RoleUserPayload } from '../../../core/models/role-user.model';
import { CrudService } from '../crud';

@Injectable({ providedIn: 'root' })
export class RoleUserApi extends CrudService<RoleUser, RoleUserPayload> {
  constructor() {
    super(`${environment.apiUrl}/user-roles`);
  }
}
