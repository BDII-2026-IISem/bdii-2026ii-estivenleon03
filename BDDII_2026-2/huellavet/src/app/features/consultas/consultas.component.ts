import { Component } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';

interface Consultation {
  id: number;
  pet_name: string;
  owner_name: string;
  reason: string;
  date: Date;
  status: string;
}

@Component({
  selector: 'app-consultas',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CardModule,
    TableModule,
    TagModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    DatePipe
  ],
  templateUrl: './consultas.component.html',
  styleUrl: './consultas.component.css'
})
export class ConsultasComponent {
  consultations: Consultation[] = [
    { id: 101, pet_name: 'Luna', owner_name: 'Carlos Pérez', reason: 'Vacunación Anual', date: new Date(), status: 'Completada' },
    { id: 102, pet_name: 'Zeus', owner_name: 'Ana Gómez', reason: 'Chequeo General', date: new Date(), status: 'Pendiente' }
  ];

  consultationDialog: boolean = false;
  detailsDialog: boolean = false;
  currentConsultation: Consultation = this.getEmptyConsultation();

  getEmptyConsultation(): Consultation {
    return { id: 0, pet_name: '', owner_name: '', reason: '', date: new Date(), status: 'Pendiente' };
  }

  openNew() {
    this.currentConsultation = this.getEmptyConsultation();
    this.consultationDialog = true;
  }

  viewDetails(item: Consultation) {
    this.currentConsultation = { ...item };
    this.detailsDialog = true;
  }

  hideDialog() {
    this.consultationDialog = false;
    this.detailsDialog = false;
  }

  saveConsultation() {
    if (!this.currentConsultation.pet_name.trim()) return;

    const newId = this.consultations.length > 0 ? Math.max(...this.consultations.map(c => c.id)) + 1 : 101;
    this.consultations.push({
      ...this.currentConsultation,
      id: newId,
      date: new Date()
    });

    this.consultations = [...this.consultations];
    this.consultationDialog = false;
  }
}
