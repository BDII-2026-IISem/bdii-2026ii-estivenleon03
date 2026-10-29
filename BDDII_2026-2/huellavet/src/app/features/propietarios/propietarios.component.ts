import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';

interface Owner {
  id: number;
  name: string;
  document: string;
  phone: string;
  email: string;
  pets_count: number;
}

@Component({
  selector: 'app-owners',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    DialogModule,
    InputTextModule
  ],
  templateUrl: './owners.component.html',
  styleUrl: './owners.component.css'
})
export class OwnersComponent {
  owners: Owner[] = [
    { id: 1, name: 'Carlos Pérez', document: '1098765432', phone: '3001234567', email: 'carlos@example.com', pets_count: 2 },
    { id: 2, name: 'Ana Gómez', document: '1087654321', phone: '3109876543', email: 'ana@example.com', pets_count: 1 },
    { id: 3, name: 'Luisa Martínez', document: '1076543210', phone: '3205554433', email: 'luisa@example.com', pets_count: 1 }
  ];

  ownerDialog: boolean = false;
  isEditMode: boolean = false;
  currentOwner: Owner = this.getEmptyOwner();

  getEmptyOwner(): Owner {
    return { id: 0, name: '', document: '', phone: '', email: '', pets_count: 0 };
  }

  openNew() {
    this.currentOwner = this.getEmptyOwner();
    this.isEditMode = false;
    this.ownerDialog = true;
  }

  editOwner(owner: Owner) {
    this.currentOwner = { ...owner };
    this.isEditMode = true;
    this.ownerDialog = true;
  }

  deleteOwner(owner: Owner) {
    this.owners = this.owners.filter(o => o.id !== owner.id);
  }

  hideDialog() {
    this.ownerDialog = false;
  }

  saveOwner() {
    if (!this.currentOwner.name.trim()) return;

    if (this.isEditMode) {
      const index = this.owners.findIndex(o => o.id === this.currentOwner.id);
      if (index !== -1) {
        this.owners[index] = { ...this.currentOwner };
      }
    } else {
      const newId = this.owners.length > 0 ? Math.max(...this.owners.map(o => o.id)) + 1 : 1;
      this.owners.push({ ...this.currentOwner, id: newId });
    }

    this.owners = [...this.owners];
    this.ownerDialog = false;
  }
}
