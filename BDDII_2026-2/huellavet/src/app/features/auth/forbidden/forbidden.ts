import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';

@Component({
  selector: 'app-forbidden',
  standalone: true,
  imports: [ButtonModule, CardModule, RouterLink],
  templateUrl: './forbidden.html',
  styleUrl: './forbidden.css',
  host: { class: 'block' },
})
export class Forbidden {
  readonly permission = inject(ActivatedRoute).snapshot.queryParamMap.get('permission');
}
