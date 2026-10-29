import { Component, effect, inject, input, output } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { TextareaModule } from 'primeng/textarea';
import { Propietario, PropietarioPayload } from '../../../core/models/propietario.model';

@Component({
  selector: 'app-propietario-form',
  standalone: true,
  imports: [ButtonModule, InputTextModule, MessageModule, ReactiveFormsModule, TextareaModule],
  templateUrl: './propietario-form.html',
  styleUrl: './propietario-form.css',
  host: { class: 'block' },
})
export class PropietarioForm {
  readonly propietario = input<Propietario | null>(null);
  readonly resetKey = input(0);
  readonly saving = input(false);

  readonly saved = output<PropietarioPayload>();
  readonly cancelled = output<void>();

  private readonly fb = inject(NonNullableFormBuilder);

  readonly form = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
    documento: ['', [Validators.required, Validators.maxLength(30)]],
    telefono: ['', [Validators.pattern(/^[0-9+()\s-]{7,30}$/)]],
    email: ['', [Validators.email, Validators.maxLength(150)]],
    direccion: ['', [Validators.maxLength(255)]],
  });

  constructor() {
    effect(() => {
      const current = this.propietario();
      this.resetKey();
      this.form.reset({
        nombre: current?.nombre ?? '',
        documento: current?.documento ?? '',
        telefono: current?.telefono ?? '',
        email: current?.email ?? '',
        direccion: current?.direccion ?? '',
      });
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const val = this.form.getRawValue();
    this.saved.emit({
      nombre: val.nombre.trim(),
      documento: val.documento.trim() || null,
      telefono: val.telefono.trim() || null,
      email: val.email.trim() || null,
      direccion: val.direccion.trim() || null,
    });
  }
}
