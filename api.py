import ipaddress
import subprocess
import asyncio
import threading
import time 
import json  
import os    

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from main_server.analyze_logs import Analyze_Logs
from main_server.llm_interaction import LLMInteraction
from connectionmanager import ConnectionManager

online_ips_cache = []

def scan_lan(network="10.29.60.0/24"):
    global online_ips_cache
    while True:
        net = ipaddress.ip_network(network, strict=False)
        temp_online = []
        for ip in net.hosts():
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)],
                                    stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                temp_online.append(str(ip))
        online_ips_cache = temp_online
        time.sleep(1)

threading.Thread(target=scan_lan, daemon=True).start()

class FileModified(BaseModel):
    file_name : str
    new_info : str

app = FastAPI()
llm = LLMInteraction()
conn_manager = ConnectionManager()
dict = {}

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await conn_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        conn_manager.disconnect(websocket)
        print("Client disconnected")

@app.post("/notify_file")
async def notify_file(file: FileModified):

    file_basename = os.path.basename(file.file_name)

    if file_basename == "access.log":
        analizer = Analyze_Logs()
        analysis_result = analizer.analyze_logs(file.new_info)
        print(f"File modified! {file.file_name}\nContent: {file.new_info}")
        
        if analysis_result.get_ip() in dict:
            dict[analysis_result.get_ip()].update(analysis_result.last_request)
        else:
            dict[analysis_result.get_ip()] = analysis_result

        llm_response = None
        if analysis_result.get_matched_rules() != []:
            llm_response = llm.ask_llm(analysis_result.to_str())
            print(f"LLM Response: {llm_response}")
        if dict[analysis_result.get_ip()].avg_rate > 3:
            dict[analysis_result.get_ip()].add_matched_rules("High request rate detected")
            llm_response = llm.ask_llm(dict[analysis_result.get_ip()].to_str())
            print(f"LLM Response: {llm_response}")
            dict[analysis_result.get_ip()].avg_rate = 0

        await conn_manager.broadcast({
            "type": "log",
            "ip_address": analysis_result.ip_address,
            "request_url": analysis_result.requested_url,
            "matched_rules": len(analysis_result.matched_rules),
        })

        llm_response = llm.ask_llm(analysis_result.to_str())
        await conn_manager.broadcast({
            "type": "threat analysis",
            "alert_title": llm_response['alert_title'],
            "alert_description": llm_response['alert_description'],
            "severity_level": llm_response['severity_level'],
            "recommended": llm_response['recommended']
        })

    elif file_basename == "eve.json":
        try:
            eve_event = json.loads(file.new_info)
            
            event_type = eve_event.get('event_type')
            timestamp = eve_event.get('timestamp')
            
            if event_type == 'flow':
                flow_data = eve_event.get('flow', {})
                
                await conn_manager.broadcast({
                    "type": "network_flow", 
                    "timestamp": timestamp,
                    "protocol": eve_event.get('app_proto', eve_event.get('proto')),
                    "source": eve_event.get('src_ip'),
                    "destination": eve_event.get('dest_ip'),
                    "port": eve_event.get('dest_port'),
                    "packets": flow_data.get('pkts_toserver'),
                    "bytes": flow_data.get('bytes_toserver'),
                    "status": flow_data.get('state')
                })
            
            elif event_type == 'alert':
                alert_data = eve_event.get('alert', {})
                
                await conn_manager.broadcast({
                    "type": "threat", 
                    "timestamp": timestamp,
                    "signature": alert_data.get('signature'),
                    "severity": alert_data.get('severity'),
                    "category": alert_data.get('category'),
                    "source": eve_event.get('src_ip'),
                    "destination": eve_event.get('dest_ip'),
                    "port": eve_event.get('dest_port')
                })
        
        except json.JSONDecodeError:
            print(f"Error: Could not decode Suricata JSON: {file.new_info}")
        except Exception as e:
            print(f"An error occurred processing eve.json: {e}")
            
    await conn_manager.broadcast({
        "type": "ip_data",
        "ip_addresses": online_ips_cache
    })

    return file