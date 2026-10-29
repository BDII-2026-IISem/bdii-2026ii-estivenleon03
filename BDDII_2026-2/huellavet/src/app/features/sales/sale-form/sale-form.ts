import { CurrencyPipe } from '@angular/common';
import { Component, computed, effect, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { InputNumberModule } from 'primeng/inputnumber';
import { MessageModule } from 'primeng/message';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { Propietario } from '../../../core/models/propietario.model';
import { Product } from '../../../core/models/product.model';
import { SaleCreatePayload } from '../../../core/models/sale.model';
import { toIsoWithOffset } from '../../../core/utils/sale-date';

export interface DraftLine {
  productId: number;
  productName: string;
  unitPrice: number;
  quantity: number;
  lineTotal: number;
  maxStock: number;
}

@Component({
  selector: 'app-sale-form',
  standalone: true,
  imports: [
    ButtonModule,
    CurrencyPipe,
    DatePickerModule,
    FormsModule,
    InputNumberModule,
    MessageModule,
    SelectModule,
    TableModule,
  ],
  templateUrl: './sale-form.html',
  styleUrl: './sale-form.css',
  host: { class: 'block' },
})
export class SaleForm {
  readonly clients = input<Propietario[]>([]);
  readonly products = input<Product[]>([]);
  readonly resetKey = input(0);
  readonly saving = input(false);
  readonly serverError = input<string | null>(null);

  readonly saved = output<SaleCreatePayload>();
  readonly cancelled = output<void>();

  readonly clientId = signal<number | null>(null);
  readonly saleDate = signal<Date>(new Date());
  readonly discounts = signal<number>(0);
  readonly selectedProductId = signal<number | null>(null);
  readonly inputQuantity = signal<number>(1);

  readonly lines = signal<DraftLine[]>([]);
  readonly draftError = signal<string | null>(null);

  readonly subtotal = computed(() =>
    this.lines().reduce((acc, l) => acc + l.lineTotal, 0)
  );

  readonly previewTotal = computed(() =>
    Math.max(0, this.subtotal() - (this.discounts() || 0))
  );

  constructor() {
    effect(() => {
      this.resetKey();
      this.clientId.set(null);
      this.saleDate.set(new Date());
      this.discounts.set(0);
      this.selectedProductId.set(null);
      this.inputQuantity.set(1);
      this.lines.set([]);
      this.draftError.set(null);
    });
  }

  addLine(): void {
    this.draftError.set(null);
    const prodId = this.selectedProductId();
    const qty = this.inputQuantity();

    if (!prodId) {
      this.draftError.set('Selecciona un producto o servicio.');
      return;
    }

    const prod = this.products().find((p) => p.id === prodId);
    if (!prod) return;

    if (!qty || qty < 1 || !Number.isInteger(qty)) {
      this.draftError.set('La cantidad debe ser un entero mayor o igual a 1.');
      return;
    }

    if (this.lines().some((l) => l.productId === prodId)) {
      this.draftError.set('El producto ya está en la venta.');
      return;
    }

    if (qty > prod.quantity) {
      this.draftError.set(`No hay suficiente stock. Máximo disponible: ${prod.quantity}.`);
      return;
    }

    const uPrice = Number(prod.price);
    const lineTotal = uPrice * qty;

    this.lines.update((old) => [
      ...old,
      {
        productId: prod.id,
        productName: prod.name,
        unitPrice: uPrice,
        quantity: qty,
        lineTotal,
        maxStock: prod.quantity,
      },
    ]);

    this.selectedProductId.set(null);
    this.inputQuantity.set(1);
  }

  removeLine(index: number): void {
    this.lines.update((old) => old.filter((_, i) => i !== index));
  }

  submit(): void {
    this.draftError.set(null);

    if (!this.clientId()) {
      this.draftError.set('Debes seleccionar un cliente/propietario.');
      return;
    }

    if (this.lines().length === 0) {
      this.draftError.set('Agrega al menos un producto a la venta.');
      return;
    }

    this.saved.emit({
      clientId: this.clientId()!,
      saleDate: toIsoWithOffset(this.saleDate()),
      discounts: (this.discounts() || 0).toFixed(2),
      items: this.lines().map((l) => ({ productId: l.productId, quantity: l.quantity })),
    });
  }
}
