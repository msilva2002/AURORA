import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-data',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './data.component.html',
  styleUrl: './data.component.css'
})
export class DataComponent implements OnInit {
  configurationData: any[] = [];
  errorMessage: string | null = null;
  apiUrl = environment.apiUrl; // Use the backend IP from environment.ts

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchConfigurationData();
  }

    // Apply syntax highlighting to the contenteditable <pre> tag
    applySyntaxHighlighting(element: any): void {
      // Pretty print the JSON string with 2 spaces indentation
      let formattedJson = JSON.stringify(this.configurationData, null, 2);
  
      // Remove leading spaces before the first bracket
      formattedJson = formattedJson.replace(/^\s*\[/, '[');
      formattedJson = formattedJson.replace(/^\s*\{/, '{');

      // Update the contenteditable field with the formatted JSON
      element.innerHTML = formattedJson;
    }
  

  fetchConfigurationData(): void {
    this.http.get<{config: any[]}>(this.apiUrl+'/datadescription')
      .subscribe({
        next: (data) => {
          // get config from response

          this.configurationData = data.config;
          console.log(this.configurationData);
          const preElement = document.querySelector('pre.json-pre');
          if (preElement) {
            this.applySyntaxHighlighting(preElement);
          }
        },
        error: (error) => {
          this.errorMessage = 'Error fetching configuration data. Please check API connection.';
          console.error('Error fetching configuration data:', error);
        }
      });
  }
  updateFeatureName(index: number, event: FocusEvent): void {
    const target = event.target as HTMLElement;
    const newValue = target.innerText.trim();
  
    if (this.configurationData[0]?.categorical_features?.[index]) {
      this.configurationData[0].categorical_features[index].name = newValue;
    }
  }

  updateConfiguration(event: any): void {
    const newContent = event.target.innerText;  // Get the content from the editable <pre> tag

    // Optionally, you can parse the content as JSON
    try {
      // Parse the new content to JSON and update the model
      this.configurationData = JSON.parse(newContent);
    } catch (e) {
      // If parsing fails, log the error and keep the original content
      console.error('Invalid JSON format:', e);
    }

    console.log('Updated configuration data:', this.configurationData);  // Log the updated data
  }


  // Function to save the updated configuration to the backend
  saveConfiguration(): void {
    // Clone and clean the config
    const cleanedConfig = JSON.parse(JSON.stringify(this.configurationData));
    
    cleanedConfig[0].categorical_features = cleanedConfig[0].categorical_features
      .filter((f: any) => f.name && f.name.trim() !== '');
  
    console.log('Cleaned configuration being sent:', cleanedConfig);
  
    this.http.put(this.apiUrl + '/datadescription', cleanedConfig, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    }).subscribe({
      next: (response) => {
        console.log('Configuration updated successfully:', response);
        //this.fetchConfigurationData();
        window.location.reload();
      },
      error: (error) => {
        console.error('Error saving configuration:', error);
      }
    });
  }

  // reset function
  resetConfiguration(): void{
    const updatedConfig = this.configurationData;

    // Verify that we are sending the updated data
    console.log('Updated configuration being sent:', updatedConfig);

    // Sending the updated configuration with the correct headers
    this.http.post(this.apiUrl+'/datadescription', {
    }).subscribe({
      next: (response) => {
        console.log('Configuration reseted successfully:', response);
        window.location.reload();
        this.fetchConfigurationData();
      },
      error: (error) => {
        console.error('Error reseting configuration:', error);
      }
    });
  }

  addFeature(): void {
    if (!this.configurationData[0]) {
      this.configurationData[0] = { categorical_features: [] };
    }
    this.configurationData[0].categorical_features.push({ name: '' });
  }
  
  removeFeature(index: number): void {
    if (this.configurationData[0]?.categorical_features?.length > index) {
      this.configurationData[0].categorical_features.splice(index, 1);
    }
  }


  downloadConfiguration(): void {

    const updatedConfig = this.configurationData;
    const blob = new Blob([JSON.stringify(updatedConfig)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'configuration.json';
    a.click();
    window.URL.revokeObjectURL(url);
  }

    // Handle drag over event
    handleDragOver(event: DragEvent): void {
      event.preventDefault();  // Necessary to allow dropping
      event.stopPropagation();
    }
  
    // Handle the drop event (when a file is dropped)
    handleDrop(event: DragEvent): void {
      event.preventDefault();  // Prevent default behavior (e.g., opening the file)
      event.stopPropagation();
  
      const files = event.dataTransfer?.files;
      if (files?.length) {
        const file = files[0];
  
        // Check if the file is a JSON file
        if (file.type === 'application/json') {
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const jsonContent = JSON.parse(reader.result as string);
              this.configurationData = jsonContent;  // Update the configuration data
              const preElement = document.querySelector('pre.json-pre');
              if (preElement) {
                this.applySyntaxHighlighting(preElement);  // Reapply syntax highlighting
              }
            } catch (e) {
              console.error("Error reading JSON file:", e);
            }
          };
          reader.readAsText(file);  // Read the file content as text
        } else {
          console.error("Please drop a valid JSON file.");
        }
      }
    }

    uploadConfiguration(event: any): void {
      const file = event.target.files[0];
      if (!file) return;
  
      // Check if the file is a JSON file
      if (file.type === 'application/json') {
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const jsonContent = JSON.parse(reader.result as string);
            this.configurationData = jsonContent;  // Update the configuration data
            const preElement = document.querySelector('pre.json-pre');
            if (preElement) {
              this.applySyntaxHighlighting(preElement);  // Reapply syntax highlighting
            }
          } catch (e) {
            console.error("Error reading JSON file:", e);
          }
        };
        reader.readAsText(file);  // Read the file content as text
      } else {
        console.error("Please upload a valid JSON file.");
      }
    }


}
