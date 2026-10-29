import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { PropietarioApi } from '../../core/services/propietario-api';
import { ProductApi } from '../../core/services/product-api';
import { SaleApi } from '../../core/services/sale-api';
import { Dashboard } from './dashboard';

describe('DashboardComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Dashboard],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: SaleApi,
          useValue: {
            list: () =>
              of([
                {
                  id: 1,
                  total: '100.00',
                  status: 'active',
                  saleDate: new Date().toISOString(),
                },
              ]),
          },
        },
        {
          provide: ProductApi,
          useValue: {
            list: () => of([{ id: 1, quantity: 2, minStock: 5, status: 'active' }]),
          },
        },
        {
          provide: PropietarioApi,
          useValue: {
            list: () => of([{ id: 1, status: 'active' }]),
          },
        },
      ],
    }).compileComponents();
  });

  it('debe calcular las 4 métricas del panel correctamente', async () => {
    const fixture = TestBed.createComponent(Dashboard);
    await fixture.whenStable();

    expect(fixture.componentInstance.todayPayments().length).toBe(1);
    expect(fixture.componentInstance.todayTotal()).toBe(100);
    expect(fixture.componentInstance.lowStockProducts().length).toBe(1);
    expect(fixture.componentInstance.activeClientsCount()).toBe(1);
  });
});
