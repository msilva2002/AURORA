import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';  // Import CommonModule for structural directives

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule],  // Add CommonModule for ngIf, ngFor
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'frontend';
}
