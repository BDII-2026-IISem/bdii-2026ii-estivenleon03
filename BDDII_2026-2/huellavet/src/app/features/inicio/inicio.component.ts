import { Component } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule, CardModule, TableModule, TagModule, DatePipe],
  templateUrl: './inicio.component.html',
  styleUrl: './inicio.component.css'
})
export class InicioComponent {
  pets = [
    {
      id: 1,
      name: 'Luna',
      species: 'Canino',
      breed: 'Labrador',
      owner_details: { name: 'Carlos Pérez', phone: '3001234567' },
      is_active: true
    }
  ];

  payments = [
    {
      id: 101,
      reference_type: 'Consulta',
      reference_id: 1,
      method: 'Efectivo',
      amount: 50000,
      payment_date: new Date(),
      status: 'PAID'
    }
  ];
}