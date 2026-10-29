import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';

interface Pet {
  id: number;
  name: string;
  species: string;
  breed: string;
  age: string;
  owner: string;
  phone: string;
  is_active: boolean;
}

@Component({
  selector: 'app-mascotas',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CardModule,
    TableModule,
    TagModule,
    ButtonModule,
    DialogModule,
    InputTextModule
  ],
  templateUrl: './mascotas.component.html',
  styleUrl: './mascotas.component.css'
})
export class MascotasComponent {
  pets: Pet[] = [
    { id: 1, name: 'Luna', species: 'Canino', breed: 'Labrador', age: '3 años', owner: 'Carlos Pérez', phone: '3001234567', is_active: true },
    { id: 2, name: 'Zeus', species: 'Canino', breed: 'Pastor Alemán', age: '5 años', owner: 'Ana Gómez', phone: '3109876543', is_active: true },
    { id: 3, name: 'Mishi', species: 'Felino', breed: 'Siamés', age: '2 años', owner: 'Luisa Martínez', phone: '3205554433', is_active: false }
  ];

  petDialog: boolean = false;
  isEditMode: boolean = false;

  currentPet: Pet = this.getEmptyPet();

  getEmptyPet(): Pet {
    return {
      id: 0,
      name: '',
      species: '',
      breed: '',
      age: '',
      owner: '',
      phone: '',
      is_active: true
    };
  }

  openNew() {
    this.currentPet = this.getEmptyPet();
    this.isEditMode = false;
    this.petDialog = true;
  }

  editPet(pet: Pet) {
    this.currentPet = { ...pet };
    this.isEditMode = true;
    this.petDialog = true;
  }

  deletePet(pet: Pet) {
    this.pets = this.pets.filter(p => p.id !== pet.id);
  }

  hideDialog() {
    this.petDialog = false;
  }

  savePet() {
    if (!this.currentPet.name.trim()) return;

    if (this.isEditMode) {
      const index = this.pets.findIndex(p => p.id === this.currentPet.id);
      if (index !== -1) {
        this.pets[index] = { ...this.currentPet };
      }
    } else {
      const newId = this.pets.length > 0 ? Math.max(...this.pets.map(p => p.id)) + 1 : 1;
      this.pets.push({ ...this.currentPet, id: newId });
    }

    this.pets = [...this.pets];
    this.petDialog = false;
  }
}
