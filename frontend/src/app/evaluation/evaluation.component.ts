import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-evaluation',
  templateUrl: './evaluation.component.html',
  styleUrls: ['./evaluation.component.css'],
  imports: [CommonModule]
})

export class EvaluationComponent implements OnInit {

  attackData: any[] = [];
  errorMessage: string = '';
  visibleEvaluations: boolean[] = [];
  apiUrl = environment.apiUrl;
  reportAvailable: boolean = false;


  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchAttackStatus();
    this.fetchReportStatus();
  }

  fetchReportStatus(): void {
    this.http.get(this.apiUrl + '/reportstatus', { observe: 'response' })
    .subscribe({
      next: (response) => {
        this.reportAvailable = response.status === 200;
      },
      error: (error) => {
        console.error('Error fetching report data:', error);
      }
    });
  }
  

  fetchAttackStatus(): void {
    this.http.get<any[]>(this.apiUrl+'/status')
      .subscribe({
        next: (data) => {
          this.attackData = data;
          this.attackData.sort((a, b) => a.attackName.localeCompare(b.attackName));
          this.errorMessage = '';
        },
        error: (error) => {
          this.errorMessage = 'Error loading data: ' + (error.message || 'Unknown error');
          console.error('Error fetching attack data:', error);
        }
      });
  }

  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  formatValue(value: any): string {
    return isNaN(value) ? 'Not Available' : value;
  }

  toggleEvaluation(index: number): void {
    this.visibleEvaluations[index] = !this.visibleEvaluations[index];
  }

  // Check if an entry is the "Confusion Matrix"
  isConfusionMatrix(entry: any): boolean {
    return entry.hasOwnProperty('Confusion Matrix');
  }

  // Check if any evaluation contains a confusion matrix
  hasConfusionMatrix(evaluations: any[]): boolean {
    return evaluations.some(entry => this.isConfusionMatrix(entry));
  }

  // Retrieve the confusion matrix from evaluations
  getConfusionMatrix(evaluations: any[]): any[] {
    const entryWithMatrix = evaluations.find(entry => this.isConfusionMatrix(entry));
    return entryWithMatrix ? entryWithMatrix['Confusion Matrix'] : [];
  }

  downloadReport(): void {
    this.http.get(`${this.apiUrl}/report`, {
      responseType: 'blob' // important for downloading files
    }).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report.zip`; // filename
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        alert('Error downloading report: ' + (error.statusText || 'Unknown error'));
      }
    });
  }

  downloadEvaluation(attackName: string): void {
    this.http.get(`${this.apiUrl}/download`, {
      params: { attackName },
      responseType: 'blob' // important for downloading files
    }).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${attackName}.csv`; // filename
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        alert('Error downloading evaluation: ' + (error.statusText || 'Unknown error'));
      }
    });
    
  }
}

