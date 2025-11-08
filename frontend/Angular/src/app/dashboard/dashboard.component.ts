import { Component, OnInit, OnDestroy, ViewChild, ElementRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgxGraphModule } from '@swimlane/ngx-graph';
import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';
import SpriteText from 'three-spritetext';
import { DashboardService } from '../service/dashboard.service';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';


interface LogEntry {
  timestamp: string,
  ip_address: string,
  request_url: string[],
  matched_rules: number;
}

interface NetworkData {
  protocol: string;
  source: string;
  destination: string;
  port: number;
  packets: number;
  timestamp: string;
};

interface Interpretation {
  timestamp: string,
 alert_title: string,
  alert_description: string,
  severity_level: string,
   recommended: string;
}

interface IPNode {
  ip: string,
  color: string,
  size: number,
}


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, NgxGraphModule,MatButtonModule, MatIconModule ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
handleHome() {
  this.router.navigate(['/home']);
this
}
  @ViewChild('networkContainer', { static: true }) networkContainer!: ElementRef<HTMLDivElement>;

ngAfterViewInit(): void {

}


  logs: LogEntry[] = [];
  networkData1: NetworkData[] = [];
  interpretations: Interpretation[] = [];
  ipNodes: IPNode[] = [];
  Math = Math;
   
  private logInterval: any;
  private networkInterval: any;

  ngOnInit() {
    this.initializeLogs();
    this.initializeNetworkData();
    this.initializeInterpretations();
    this.initializeIPGraph();
    this.service.connect();
  }

  ngOnDestroy() {
    if (this.logInterval) clearInterval(this.logInterval);
    if (this.networkInterval) clearInterval(this.networkInterval);
  }
  rawIPs : string[] = [];
  constructor(private service:DashboardService,private router: Router) {}

  private initializeLogs() {
    this.service.logs.subscribe({ next: (value) => {this.logs.push({timestamp: this.getTimestamp(),ip_address: value.ip_address, request_url: value.request_url, matched_rules: value.matched_rules}); if(this.logs.length > 100) this.logs.shift();},
  error: (err)=> console.log(err)});
  }

validate(object: any): boolean {
    for (const obj of this.networkData1) {
      if(obj.protocol === object.protocol && obj.source === object.source &&
         obj.destination === object.destination && obj.port === object.port) {
        return false;
      }
    }
          return true;
  }
  
  private initializeNetworkData() {
    this.service.networkData.subscribe({ next: (value) => { if(this.validate(value)){this.networkData1.push({timestamp: this.getTimestamp(), protocol: value.protocol, source: value.source, destination: value.destination, port: value.port, packets: value.packets})}},
  error: (err)=> console.log(err)});
    

  }
  private initializeInterpretations() {
    this.service.threadAnalysis.subscribe({ next: (value) => { this.interpretations.push({alert_title: value.alert_title, alert_description: value.alert_description, severity_level: value.severity_level,recommended: value.recommended,timestamp: value.timestamp}); if(this.interpretations.length > 100) this.interpretations.shift();},
  error: (err)=> console.log(err)});
  }
private initializeIPGraph() {
  this.service.ips.subscribe({
    next: (value) => {

      // eliminăm duplicatele
      this.rawIPs = Array.from(new Set([...this.rawIPs, ...value]));

      const routerNodeId = "Router";

      const nodes: any[] = [
        { id: routerNodeId, color: 'green', size: 3 }  // router
      ];

      // IP nodes
      for (let ip of this.rawIPs) {
        nodes.push({
          id: ip,
          color: '#4a90e2',
          size: 1
        });
      }

      // Links
      const links = this.rawIPs.map(ip => ({
        source: routerNodeId,
        target: ip
      }));

      const container = this.networkContainer.nativeElement;

      const Graph3D = new ForceGraph3D(container)
        .graphData({ nodes, links })
        .nodeThreeObject((node: any) => {
          const sphere = new THREE.Mesh(
            new THREE.SphereGeometry(node.size, 16, 16),
            new THREE.MeshStandardMaterial({ color: node.color })
          );

          const sprite = new SpriteText(node.id);
          sprite.color = '#ffffff';
          sprite.textHeight = node.size * 0.8;
          sprite.position.set(0, node.size + 0.5, 0);

          const group = new THREE.Group();
          group.add(sphere);
          group.add(sprite);
          return group;
        })
        .linkWidth(2)
        .linkColor(() => 'rgba(0,255,255,0.4)')
        .enableNodeDrag(true);

      // lighting
      const light = new THREE.PointLight(0xffffff, 1);
      light.position.set(0, 10, 10);
      Graph3D.scene().add(light);

      Graph3D.width(container.clientWidth);
      Graph3D.height(container.clientHeight);

      Graph3D.cameraPosition(
        { x: 0, y: 40, z: 60 },
        { x: 0, y: 0, z: 0 },
        2000
      );
    },
    error: (err) => console.log(err)
  });
}



  public getTimestamp(offsetSeconds: number = 0): string {
    const date = new Date(Date.now() + offsetSeconds * 1000);
    return date.toISOString().replace('T', ' ').substring(0, 19);
  }

  getLogClass(level: string): string {
    return `log-${level}`;
  }

  getSeverityClass(severity: string): string {
    return `severity-${severity}`;
  }
}
