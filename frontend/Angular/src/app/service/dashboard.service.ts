import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/internal/Subject';
interface LogEntry {
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
 alert_title: string,
 alert_description: string,
 severity_level: string,
 recommended: string

}

interface IPNode {
  ip_addresses: string[];
}
@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private ws!: WebSocket;
  public logs = new Subject<any>();
  public networkData = new Subject<any>();
  public threadAnalysis = new Subject<any>();
  public ips = new Subject<any>();

  async connect(): Promise<void> {


    this.ws = new WebSocket(`ws://10.29.60.233:8000/ws`);
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.ws.send(JSON.stringify({ message: "Salut server!" }));
    };
    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const message: any = JSON.parse(event.data);
        if(message.type === 'log') {
          let  data : LogEntry = {ip_address : message.ip_address, request_url : message.request_url, matched_rules : message.matched_rules};
          this.logs.next(data);
        } else if(message.type === 'network_flow') {
          let data : NetworkData = {protocol: message.protocol, source: message.source, destination: message.destination, port: message.port, packets: message.packets, timestamp: message.timestamp};
          this.networkData.next(data);
        } else if(message.type === 'threat analysis') {
          let data : Interpretation = {alert_title : message.alert_title, alert_description : message.alert_description, severity_level : message.severity_level , recommended : message.recommended};
          this.threadAnalysis.next(data);
        } else if(message.type === 'ip_data') {
          this.ips.next(message.ip_addresses);
        }
        console.log(message)
      } catch (err) {
        console.error('Invalid WS message', err, event.data);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected. Trying to reconnect in 3s...');
      setTimeout(() => this.connect(), 3000); 
    };

  
    this.ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }
}