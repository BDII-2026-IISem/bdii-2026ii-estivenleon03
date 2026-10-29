import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { User } from '../../../core/models/user.model';
import { UserApi } from './user-api';

const MOCK_USER: User = {
  id: 1,
  username: 'admin',
  email: 'admin@test.com',
  avatar: null,
  status: 'active',
};

describe('UserApi', () => {
  let api: UserApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(UserApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('debe leer usuarios sin incluir el campo password en el modelo', () => {
    let rows: User[] = [];
    api.list().subscribe((data) => (rows = data));

    const req = http.expectOne('http://localhost:8000/api/users/');
    req.flush([MOCK_USER]);

    expect(Object.keys(rows[0])).not.toContain('password');
  });

  it('no debe enviar password durante un PATCH de actualización', () => {
    api
      .update(1, { username: 'admin', email: 'admin@test.com', avatar: null, status: 'active' })
      .subscribe();

    const patch = http.expectOne('http://localhost:8000/api/users/1/');
    expect(patch.request.method).toBe('PATCH');
    expect('password' in (patch.request.body as object)).toBe(false);
    patch.flush(MOCK_USER);
  });
});
