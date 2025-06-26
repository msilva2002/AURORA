import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-configuration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css']
})
export class ConfigurationComponent implements OnInit {
  configurationData: any[] = [];
  errorMessage: string | null = null;
  apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchConfigurationData();
  }


  fetchConfigurationData(): void {
    const savedExpandedStates = JSON.parse(localStorage.getItem('expandedStates') || '[]');
  
    this.http.get<{ config: any[] }>(this.apiUrl + '/configuration')
      .subscribe({
        next: (data) => {
          this.configurationData = data.config.map((item, index) => ({
            ...item,
            expanded: savedExpandedStates[index] || false
          }));
  
          console.log('Fetched data:', this.configurationData);
  
          // Clear after applying
          localStorage.removeItem('expandedStates');
        },
        error: (error) => {
          this.errorMessage = 'Error fetching configuration data. Please check API connection.';
          console.error('Error fetching configuration data:', error);
        }
      });
  }

  hasNonNestedValues(item: any): boolean {
    return this.objectKeys(item).some(key =>
      key !== 'attackName' &&
      key !== 'expanded' &&
      !this.isArrayOfObjects(item[key])
    );
  }

  removeNestedRow(parentIndex: number, key: string, objIndex: number): void {
    const list = this.configurationData[parentIndex][key];
    if (Array.isArray(list) && list.length > 1) {
      this.configurationData[parentIndex][key].splice(objIndex, 1);
    }
  }

  getDefaultCategoricalRow(): any {
    return {
      features : "",
      locked_features : "",
      probability : "",
      type : "combination"
    };
  }
  
  getDefaultNumericalRow(): any {
    return {
      features : "",
      probability : "",
      type : "interval",
      integer_features : "",
      max_ratio : "",
      missing_value : "",
      ratio : ""
    };
  }

  addCategoricalRow(parentIndex: number, key: string): void {
    const newRow = this.getDefaultCategoricalRow();
    this.configurationData[parentIndex][key].push(newRow);
  }
  
  addNumericalRow(parentIndex: number, key: string): void {
    const newRow = this.getDefaultNumericalRow();
    this.configurationData[parentIndex][key].push(newRow);
  }
  
  
  
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }
  
  isArrayOfObjects(value: any): boolean {
    return Array.isArray(value) && value.every(v => typeof v === 'object' && v !== null && !Array.isArray(v));
  }
  
  getAllKeys(obj: any): string[] {
    const keySet = new Set<string>();
    if (Array.isArray(obj)) {
      obj.forEach(o => Object.keys(o || {}).forEach(k => keySet.add(k)));
    } else {
      Object.keys(obj || {}).forEach(k => keySet.add(k));
    }
    return Array.from(keySet);
  }

  
  handleNestedBlur(itemIndex: number, key: string, objIndex: number, subKey: string, event: FocusEvent): void {
    const target = event.target as HTMLElement;
    const newValue = target.innerText.trim();
    const original = this.configurationData[itemIndex][key][objIndex][subKey];
  
    // Default: string
    let parsedValue: any = newValue;
  
    // If it looks like a number, store as number
    if (!isNaN(Number(newValue)) && newValue !== '') {
      parsedValue = Number(newValue);
    }
  
    // Update only if value has changed
    if (original !== parsedValue) {
      this.configurationData[itemIndex][key][objIndex][subKey] = parsedValue;
    }
  }
  
  

  onEdit(index: number, key: string, newValue: string): void {
    this.configurationData[index][key] = newValue.trim();
  }

  handleBlur(index: number, key: string, event: FocusEvent): void {
    const target = event.target as HTMLElement;
    const newValue = target.innerText.trim();
    this.onEdit(index, key, newValue);
  }


  isFullyFilled(obj: any): boolean {
    if (typeof obj !== 'object' || obj === null) return false;
  
    const allowedEmptyKeysAlways = ['locked_features', 'integer_features'];
  
    const isValueFilled = (value: any): boolean => {
      if (value === null || value === undefined) return false;
      if (typeof value === 'string') return value.trim() !== '';
      return true;
    };
  
    for (const key of Object.keys(obj)) {
      if (key === 'expanded' || key === 'attackName') continue;
      if (allowedEmptyKeysAlways.includes(key)) continue;
  
      // Allow feature_label to be empty only if it's a general config (no attackName)
      if (key === 'feature_label' && !obj['attackName']) continue;
  
      const value = obj[key];
  
      if (Array.isArray(value)) {
        if (this.isArrayOfObjects(value)) {
          if (
            value.length === 0 ||
            value.some((item: any) => !this.isFullyFilled(item))
          ) {
            return false;
          }
        }
      } else if (!isValueFilled(value)) {
        return false;
      }
    }
  
    return true;
  }


  saveConfiguration(): void {
    const updatedConfig = this.configurationData;
  
    const allFilled = updatedConfig.every(configItem => this.isFullyFilled(configItem));
  
    if (!allFilled) {
      this.errorMessage = 'Please fill out all fields before saving.';
      // error message as alert
      alert(this.errorMessage);
      return;
    }
  
    console.log('Updated configuration being sent:', updatedConfig);
  
    const expandedState = this.configurationData.map(item => item.expanded);
    localStorage.setItem('expandedStates', JSON.stringify(expandedState));

    const sanitizedConfig = updatedConfig.map(({ expanded, ...rest }) => ({ ...rest }));
  
    this.http.put(this.apiUrl + '/configuration', sanitizedConfig, {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    }).subscribe({
      next: (response) => {
        console.log('Configuration updated successfully:', response);
        window.location.reload();
      },
      error: (error) => {
        console.error('Error saving configuration:', error);
      }
    });
  }
  

  resetConfiguration(): void {
    // Save expanded state
    const expandedState = this.configurationData.map(item => item.expanded);
    localStorage.setItem('expandedStates', JSON.stringify(expandedState));
  
    this.http.post(this.apiUrl + '/configuration', {}).subscribe({
      next: (response) => {
        console.log('Configuration reset successfully:', response);
        window.location.reload();
      },
      error: (error) => {
        console.error('Error resetting configuration:', error);
      }
    });
  }

  downloadConfiguration(): void {
    const updatedConfig = this.configurationData.map(({ expanded, ...rest }) => rest);
    
    const blob = new Blob([JSON.stringify(updatedConfig, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'configuration.json';
    a.click();
    window.URL.revokeObjectURL(url);
  }

  uploadConfiguration(event: any): void {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type === 'application/json') {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const jsonContent = JSON.parse(reader.result as string);
          this.configurationData = jsonContent.map((item: any) => ({ ...item, expanded: false }));
          this.saveConfiguration();
        } catch (e) {
          console.error("Error reading JSON file:", e);
          this.errorMessage = 'Failed to parse the JSON file. Please check the file content.';
        }
      };
      reader.readAsText(file);
    } else {
      console.error("Please upload a valid JSON file.");
      this.errorMessage = 'Please upload a valid JSON file.';
    }
  }
}
