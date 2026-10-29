import { Injectable } from '@angular/core';
import { environment } from '../../../../environments/environment';
import { Role, RolePayload } from '../../../core/models/role.model';
import { CrudService } from '../crud';

@Injectable({ providedIn: 'root' })
export class RoleApi extends CrudService<Role, RolePayload> {
  constructor() {
    super(`${environment.apiUrl}/roles`);
  }
}
