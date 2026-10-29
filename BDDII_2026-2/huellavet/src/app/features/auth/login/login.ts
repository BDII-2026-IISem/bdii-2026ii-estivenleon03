import { Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { PasswordModule } from 'primeng/password';
import { LoginRequest } from '../../../core/models/auth.model';
import { AuthService } from '../../../core/services/auth';
import { toApiMessage } from '../../../core/utils/to-api-message';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    ButtonModule,
    CardModule,
    InputTextModule,
    MessageModule,
    PasswordModule,
  ],
  templateUrl: './login.html',
  styleUrl: './login.css',
  host: { class: 'block' },
})
export class Login {
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  readonly form = this.fb.group({
    identifier: ['', [Validators.required]],
    password: ['', [Validators.required]],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading.set(true);
    this.error.set(null);

    const { identifier, password } = this.form.getRawValue();
    const value = identifier.trim();
    const credentials: LoginRequest = value.includes('@')
      ? { email: value, password }
      : { username: value, password };

    this.auth.login(credentials).subscribe({
      next: () => {
        void this.router.navigateByUrl(this.returnUrl());
      },
      error: (err: unknown) => {
        this.loading.set(false);
        this.error.set(toApiMessage(err));
      },
    });
  }

  private returnUrl(): string {
    const requested = this.route.snapshot.queryParamMap.get('returnUrl') ?? '/dashboard';
    return requested.startsWith('/') && !requested.startsWith('/login')
      ? requested
      : '/dashboard';
  }
}
