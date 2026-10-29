import { Injectable } from '@angular/core';
import { environment } from '../../../../environments/environment';
import { ResourceRole, ResourceRolePayload } from '../../../core/models/resource-role.model';
import { CrudService } from '../crud';

@Injectable({ providedIn: 'root' })
export class ResourceRoleApi extends CrudService<ResourceRole, ResourceRolePayload> {
  constructor() {
    super(`${environment.apiUrl}/role-permissions`);
  }
}
