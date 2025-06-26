// path.component.ts
import { Component, AfterViewInit, ViewChild, ElementRef, HostListener } from '@angular/core';

@Component({
  selector: 'app-path',
  standalone: true,
  templateUrl: './path.component.html',
  styleUrls: ['./path.component.css']
})
export class PathComponent implements AfterViewInit {
  @ViewChild('connectors', { static: false }) connectors!: ElementRef<SVGSVGElement>;
  private svgElements: SVGElement[] = [];

  ngAfterViewInit() {
    this.drawAllConnectors();
  }

  private drawConnector(fromId: string, toId: string, number: string) {
    const from = document.getElementById(fromId);
    const to = document.getElementById(toId);
    if (!from || !to || !this.connectors) return;
  
    const fromRect = from.getBoundingClientRect();
    const toRect = to.getBoundingClientRect();
    const containerRect = this.connectors.nativeElement.getBoundingClientRect();
  
    const x1 = fromRect.left + fromRect.width / 2 - containerRect.left;
    const y1 = fromRect.top + fromRect.height / 2 - containerRect.top;
    const x2 = toRect.left + toRect.width / 2 - containerRect.left;
    const y2 = toRect.top + toRect.height / 2 - containerRect.top;
  
    // Create the line
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1.toString());
    line.setAttribute('y1', y1.toString());
    line.setAttribute('x2', x2.toString());
    line.setAttribute('y2', y2.toString());
    line.setAttribute('stroke', '#3498db');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('marker-end', 'url(#arrowhead)');
  
    // Append the line
    this.connectors.nativeElement.appendChild(line);
    this.svgElements.push(line);
  
    // Calculate midpoint
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
  
    // Create the text label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', midX.toString());
    text.setAttribute('y', midY.toString());
    text.setAttribute('fill', 'black');
    text.setAttribute('font-size', '14');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('alignment-baseline', 'middle');
    text.textContent = number;
  
    // Optional: offset vertically so it's not exactly on the line
    text.setAttribute('dy', '-6'); // slight upward shift
  
    // Append the label
    this.connectors.nativeElement.appendChild(text);
    this.svgElements.push(text);
  }
  

  private drawAllConnectors() {
    this.clearConnectors();
    this.drawConnector('discover', 'craft', '1');
    this.drawConnector('craft', 'evade', '2');
    this.drawConnector('craft', 'quality', '2');
    this.drawConnector('evade', 'metrics', '3');
    this.drawConnector('quality', 'metrics', '3');
    this.drawConnector('metrics', 'robustness', '4');
  }

  private clearConnectors() {
    this.svgElements.forEach(line => line.remove());
    this.svgElements = [];
  }

  @HostListener('window:resize')
  onResize() {
    this.drawAllConnectors();
  }
}