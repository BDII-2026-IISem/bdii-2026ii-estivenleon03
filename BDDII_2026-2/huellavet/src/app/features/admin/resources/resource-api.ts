import { Injectable } from '@angular/core';
import { environment } from '../../../../environments/environment';
import { Resource, ResourcePayload } from '../../../core/models/resource.model';
import { CrudService } from '../crud';

@Injectable({ providedIn: 'root' })
export class ResourceApi extends CrudService<Resource, ResourcePayload> {
  constructor() {
    super(`${environment.apiUrl}/permissions`);
  }
}
