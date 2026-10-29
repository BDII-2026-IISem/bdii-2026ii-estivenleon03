import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  host: { class: 'block' },
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}
