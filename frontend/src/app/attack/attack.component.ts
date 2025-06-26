import { Component, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-attack',
  templateUrl: './attack.component.html',
  styleUrls: ['./attack.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})

export class AttackComponent {
  selectedModelFile: File | null = null;
  selectedDatasetFile: File | null = null;
  selectedTargetFile: File | null = null;
  apiUrl = environment.apiUrl; // Use the backend IP from environment.ts


  constructor(private cdr: ChangeDetectorRef, private http:HttpClient) {}

  handleFileInput(event: Event, type: 'model' | 'dataset' | 'target') {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      const file = target.files[0];

      if (type === 'model') {
        this.selectedModelFile = file;
      } else if (type === 'dataset') {
        this.selectedDatasetFile = file;
      } else if (type === 'target') {
        this.selectedTargetFile = file;
      }

      this.cdr.detectChanges(); // Ensures UI updates immediately
    }
  }

  startAttack() {
    if (!this.selectedDatasetFile) {
      alert("No dataset file selected!");
      return;
    }

    const formData = new FormData();
  
    // Append model file or empty blob if null
    formData.append('model', this.selectedModelFile || new Blob([], { type: 'application/octet-stream' }));
    
    // Append dataset file
    formData.append('dataset', this.selectedDatasetFile);
    
    // Append target file or empty blob if null
    formData.append('target', this.selectedTargetFile || new Blob([], { type: 'application/octet-stream' }));
  
    // Send the form data to your API
    this.http.post<{ message: string }>(this.apiUrl+'/start', formData)
    .subscribe({
      next: (response) => {
        console.log('Success:', response);
        alert(response.message);  // Show "Started" message from backend
      },
      error: (error) => {
        console.error('Error:', error);  // Debugging
  
        // Extract and display backend error message
        if (error.error && error.error.error) {
          alert('Failed to start attack. ' + error.error.error);
        } else {
          alert('Failed to start attack. Unknown error.');
        }
      }
    });
  }
}
